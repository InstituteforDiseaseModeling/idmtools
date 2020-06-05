import functools
import logging
import time
from dataclasses import dataclass
from logging import getLogger
from math import floor
from typing import List, Any, Dict, Container, NoReturn
from uuid import UUID
from tqdm import tqdm
from idmtools.assets import Asset
from idmtools.core.docker_task import ContainerTask
from idmtools.core.experiment_factory import experiment_factory
from idmtools.entities.experiment import Experiment
from idmtools.entities.iplatform_ops.iplatform_experiment_operations import IPlatformExperimentOperations
from idmtools.entities.simulation import Simulation
from idmtools_platform_local.client.experiments_client import ExperimentsClient
from idmtools_platform_local.client.simulations_client import SimulationsClient
from idmtools_platform_local.platform_operations.uitils import local_status_to_common, ExperimentDict, SimulationDict

logger = getLogger(__name__)


@dataclass
class LocalPlatformExperimentOperations(IPlatformExperimentOperations):
    platform: 'LocalPlatform'  # noqa F821
    platform_type: type = ExperimentDict

    def get(self, experiment_id: UUID, **kwargs) -> ExperimentDict:
        """
        Get the experiment object by id

        Args:
            experiment_id: Id
            **kwargs:

        Returns:
            Experiment Dict object
        """
        experiment_dict = ExperimentsClient.get_one(str(experiment_id))
        return ExperimentDict(experiment_dict)

    def platform_create(self, experiment: Experiment, **kwargs) -> Dict:
        """
        Create an experiment.

        Args:
            experiment: Experiment to create
            **kwargs:

        Returns:
            Created experiment object and UUID
        """
        from idmtools_platform_local.internals.tasks.create_experiment import CreateExperimentTask
        from dramatiq.results import ResultTimeout
        if not self.platform.are_requirements_met(experiment.platform_requirements):
            raise ValueError("One of the requirements not supported by platform")

        m = CreateExperimentTask.send(experiment.tags)

        # Create experiment is vulnerable to disconnects early on of redis errors. Lets do a retry on conditions
        start = time.time()
        timeout_diff = 0
        if self.platform.heartbeat_timeout < self.platform.default_timeout:
            time_increment = self.platform.heartbeat_timeout
        else:
            time_increment = self.platform.default_timeout
        while self.platform.default_timeout - timeout_diff > 0:
            try:
                eid = m.get_result(block=True, timeout=time_increment * 1000)
                break
            except ResultTimeout as e:
                logger.debug('Resetting broker client because of a heartbeat failure')
                timeout_diff = floor(time.time() - start)
                self.platform._sm.restart_brokers(self.platform.heartbeat_timeout)
                if timeout_diff >= self.platform.default_timeout:
                    logger.exception(e)
                    logger.error("Could not connect to redis")
                    raise e

        experiment.uid = eid
        path = "/".join(["/data", experiment.uid, "Assets"])

        self.platform._do.create_directory(path)
        self.send_assets(experiment)
        if self.platform.launch_created_experiments_in_browser:
            self._launch_item_in_browser(experiment)
        return self.from_experiment(experiment)

    def get_children(self, experiment: Dict, **kwargs) -> List[SimulationDict]:
        """
        Get children for an experiment

        Args:
            experiment: Experiment to get chidren for
            **kwargs:

        Returns:
            List of simulation dicts
        """
        # Retrieve the simulations for the current page
        simulations = SimulationsClient.get_all(experiment_id=experiment['experiment_id'], per_page=9999)
        return [SimulationDict(s) for s in simulations]

    def get_parent(self, experiment: Any, **kwargs) -> None:
        """
        Experiment on local platform have no parents so return None

        Args:
            experiment:
            **kwargs:

        Returns:

        """
        return None

    def platform_run_item(self, experiment: Experiment, **kwargs):
        """
        Run the experiment

        Args:
            experiment: experiment to run

        Returns:

        """
        for simulation in tqdm(experiment.simulations, desc="Running Simulations"):
            # if the task is docker, build the extra config
            if simulation.task.is_docker:
                self._run_docker_sim(experiment.uid, simulation.uid, simulation.task)
            else:
                from idmtools_platform_local.internals.tasks.general_task import RunTask
                logger.debug(f"Running simulation: {simulation.uid}")
                RunTask.send(simulation.task.command.cmd, experiment.uid, simulation.uid)

    def send_assets(self, experiment: Experiment, **kwargs):
        """

        Sends assets for specified experiment

        Args:
            experiment: Experiment to send assets for

        Returns:

        """
        # Go through all the assets
        path = "/".join(["/data", experiment.uid, "Assets"])
        # get worker container
        worker = self.platform._sm.get('workers')
        list(map(functools.partial(self._send_asset_to_docker, path=path, worker=worker), experiment.assets))

    def refresh_status(self, experiment: Experiment, **kwargs):
        """
        Refresh status of experiment

        Args:
            experiment: Experiment to refresh status for

        Returns:

        """
        status = SimulationsClient.get_all(experiment_id=experiment.uid, per_page=9999)
        for s in experiment.simulations:
            sim_status = [st for st in status if st['simulation_uid'] == s.uid]

            if sim_status:
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f"Simulation {sim_status[0]['simulation_uid']}status: {sim_status[0]['status']}")
                s.status = local_status_to_common(sim_status[0]['status'])

    @staticmethod
    def from_experiment(experiment: Experiment) -> Dict:
        """
        Create a experiment dictionary from Experiment object

        Args:
            experiment: Experiment object

        Returns:
            Experiment as a local platform dict
        """
        e = dict(experiment_id=experiment.uid, tags=experiment.tags)
        return e

    def to_entity(self, experiment: Dict, **kwargs) -> Experiment:
        """
        Convert an ExperimentDict to an Experiment

        Args:
            experiment: Experiment to convert
            **kwargs:

        Returns:
            object as an IExperiment object
        """
        e = experiment_factory.create(experiment['tags'].get("type"), tags=experiment['tags'])
        e.platform = self.platform
        e.uid = experiment['experiment_id']
        return e

    def _run_docker_sim(self, experiment_uid: UUID, simulation_uid: UUID, task: ContainerTask):
        """
        Run a docker based simulation

        Args:
            experiment: Experiment to run
            simulation: Simulation to run

        Returns:

        """
        from idmtools_platform_local.internals.tasks.docker_run import DockerRunTask, GPURunTask
        logger.debug(f"Preparing Docker Task Configuration for {experiment_uid}:{simulation_uid}")
        run_cmd = GPURunTask if task.use_nvidia_run else DockerRunTask
        docker_config = dict(
            image=task.image_name,
            auto_remove=self.platform.auto_remove_worker_containers
        )
        # if we are running gpu, use nvidia runtime
        if task.use_nvidia_run:
            docker_config['runtime'] = 'nvidia'
        run_cmd.send(task.command.cmd, experiment_uid, simulation_uid, docker_config)

    def _launch_item_in_browser(self, item):
        """
        Launch experiment data page in a web browser

        Args:
            item:

        Returns:

        """
        if isinstance(item, Experiment):
            t_str = item.uid
        elif isinstance(item, Simulation):
            t_str = f'{item.parent_id}/{item.uid}'
        else:
            raise NotImplementedError("Only launching experiments and simulations is supported")
        try:
            import webbrowser
            from idmtools_platform_local.config import get_api_path
            webbrowser.open(f'{get_api_path().replace("/api", "/data")}/{t_str}?sort_by=modified&order=desc')
        except Exception:
            pass

    def _send_asset_to_docker(self, asset: Asset, path: str, worker: Container = None) -> NoReturn:
        """
        Handles sending an asset to docker.

        Args:
            asset: Asset object to send
            path: Path to send find to within docker container
            worker: Optional worker to reduce docker calls

        Returns:
            (NoReturn): Nada
        """
        file_path = asset.absolute_path
        remote_path = "/".join([path, asset.relative_path]) if asset.relative_path else path
        # ensure remote directory exists
        result = self.platform._do.create_directory(remote_path)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Creating directory {remote_path} result: {str(result)}")
        # is it a real file?
        if worker is None:
            worker = self.platform._sm.get('workers')
        src = dict()
        if file_path:
            src['file'] = file_path
        else:
            src['content'] = asset.content
        src['dest_name'] = asset.filename if asset.filename else file_path
        self.platform._do.copy_to_container(worker, remote_path, **src)
