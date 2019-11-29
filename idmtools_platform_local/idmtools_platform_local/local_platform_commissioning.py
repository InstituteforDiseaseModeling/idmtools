import time
from dataclasses import dataclass
from logging import getLogger
from math import floor
from typing import NoReturn, List
from uuid import UUID
from idmtools.core import ItemType
from idmtools.core.interfaces.ientity import IEntityList
from idmtools.core.interfaces.iitem import IItemList
from idmtools.entities import ISimulation
from idmtools.entities.iexperiment import IDockerExperiment, IGPUExperiment, IExperiment
from idmtools.entities.iplatform import IPlatformCommissioningOperations
from idmtools_platform_local.infrastructure.service_manager import DockerServiceManager

logger = getLogger(__name__)


@dataclass(init=False)
class LocalPlatformCommissioningOperations(IPlatformCommissioningOperations):
    parent: 'LocalPlatform'
    _sm: DockerServiceManager

    def __init__(self, parent: 'LocalPlatform', sm: DockerServiceManager):
        self.parent = parent
        self._sm = sm

    def run_items(self, items: IItemList) -> NoReturn:
        from idmtools_platform_local.internals.tasks.general_task import RunTask
        for item in items:
            if item.item_type == ItemType.EXPERIMENT:
                if not self.parent.is_supported_experiment(item):
                    raise ValueError("This experiment type is not support on the LocalPlatform.")
                is_docker_type = isinstance(item, IDockerExperiment)
                for simulation in item.simulations:
                    # if the task is docker, build the extra config
                    if is_docker_type:
                        self.run_docker_sim(item, simulation)
                    else:
                        logger.debug(f"Running simulation: {simulation.uid}")
                        RunTask.send(item.command.cmd, item.uid, simulation.uid)
            else:
                raise Exception(f'Unable to run item id: {item.uid} of type: {type(item)} ')

    def _create_batch(self, batch: IEntityList, item_type: ItemType) -> List[UUID]:  # noqa: F821
        if item_type == ItemType.SIMULATION:
            ids = self._create_simulations(simulations_batch=batch)
        elif item_type == ItemType.EXPERIMENT:
            ids = [self._create_experiment(experiment=item) for item in batch]

        return ids

    def run_docker_sim(self, item, simulation):
        from idmtools_platform_local.internals.tasks.docker_run import DockerRunTask, GPURunTask
        logger.debug(f"Preparing Docker Task Configuration for {item.uid}:{simulation.uid}")
        is_gpu = isinstance(item, IGPUExperiment)
        run_cmd = GPURunTask if is_gpu else DockerRunTask
        docker_config = dict(
            image=item.image_name,
            auto_remove=self.parent.auto_remove_worker_containers
        )
        # if we are running gpu, use nvidia runtime
        if is_gpu:
            docker_config['runtime'] = 'nvidia'
        run_cmd.send(item.command.cmd, item.uid, simulation.uid, docker_config)

    def _create_simulations(self, simulations_batch: List[ISimulation]):
        """
        Create a set of simulations

        Args:
            simulations_batch: List of simulations to create

        Returns:
            Ids of simulations created
        """
        from idmtools_platform_local.internals.tasks.create_simulation import CreateSimulationsTask
        worker = self._sm.get('workers')

        m = CreateSimulationsTask.send(simulations_batch[0].experiment.uid, [s.tags for s in simulations_batch])
        ids = m.get_result(block=True, timeout=self.parent.default_timeout * 1000)

        items = dict()
        # update our uids and then build a list of files to copy
        for i, simulation in enumerate(simulations_batch):
            simulation.uid = ids[i]
            path = "/".join(["/data", simulation.experiment.uid, simulation.uid])
            items.update(self.parent.io.assets_to_copy_multiple_list(path, simulation.assets))
        result = self.parent.io.copy_multiple_to_container(worker, items)
        if not result:
            raise IOError("Coping of data for simulations failed.")
        return ids

    def _create_experiment(self, experiment: IExperiment):
        """
        Creates the experiment object on the LocalPlatform
        Args:
            experiment: Experiment object to create

        Returns:
            Id
        """
        from idmtools_platform_local.internals.tasks.create_experiment import CreateExperimentTask
        from dramatiq.results import ResultTimeout
        if not self.parent.is_supported_experiment(experiment):
            raise ValueError("This experiment type is not support on the LocalPlatform.")

        m = CreateExperimentTask.send(experiment.tags, experiment.simulation_type)

        # Create experiment is vulnerable to disconnects early on of redis errors. Lets do a retry on conditions
        start = time.time()
        timeout_diff = 0
        if self.parent.heartbeat_timeout < self.parent.default_timeout:
            time_increment = self.parent.heartbeat_timeout
        else:
            time_increment = self.parent.default_timeout
        while self.parent.default_timeout - timeout_diff > 0:
            try:
                eid = m.get_result(block=True, timeout=time_increment * 1000)
                break
            except ResultTimeout as e:
                logger.debug('Resetting broker client because of a heartbeat failure')
                timeout_diff = floor(time.time() - start)
                self._sm.restart_brokers(self.heartbeat_timeout)
                if timeout_diff >= self.default_timeout:
                    logger.exception(e)
                    logger.error("Could not connect to redis")
                    raise e
        experiment.uid = eid
        path = "/".join(["/data", experiment.uid, "Assets"])
        self.parent.io.create_directory(path)
        self.parent.io.send_assets_for_experiment(experiment)
        if self.parent.launch_created_experiments_in_browser:
            self.launch_item_in_browser(experiment)
        return experiment.uid

    def launch_item_in_browser(self, item):
        if isinstance(item, IExperiment):
            t_str = item.uid
        elif isinstance(item, ISimulation):
            t_str = f'{item.parent_id}/{item.uid}'
        else:
            raise NotImplementedError("Only launching experiments and simulations is supported")
        try:
            import webbrowser
            from idmtools_platform_local.config import get_api_path
            webbrowser.open(f'{get_api_path().replace("/api", "/data")}/{t_str}?sort_by=modified&order=desc')
        except Exception:
            pass
