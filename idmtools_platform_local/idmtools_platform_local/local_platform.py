import dataclasses
import functools
import logging
import os
import tempfile
from logging import getLogger
from typing import Optional

from dataclasses import dataclass

from idmtools.assets import Asset
from idmtools.entities import IExperiment, IPlatform
# we have to import brokers so that the proper configuration is achieved for redis
from idmtools_platform_local.client.simulations_client import SimulationsClient
from idmtools_platform_local.docker.DockerOperations import DockerOperations

status_translate = dict(
    created='CREATED',
    in_progress='RUNNING',
    canceled='canceled',
    failed='FAILED',
    done='SUCCEEDED'
)


def local_status_to_common(status):
    from idmtools.core import EntityStatus
    return EntityStatus[status_translate[status]]

logger = getLogger(__name__)


@dataclass
class LocalPlatform(IPlatform):
    auto_remove: bool = True
    network: str = 'idmtools'
    redis_image: str = 'redis:5.0.4-alpine'
    redis_port: int = 6379
    runtime: Optional[str] = None
    redis_mem_limit: str = '128m'
    redis_mem_reservation: str = '64m'
    postgres_image: str = 'postgres:11.4'
    postgres_mem_limit: str = '64m'
    postgres_mem_reservation: str = '32m'
    postgres_port: Optional[str] = 5432
    workers_image: str = 'idm-docker-staging.packages.idmod.org:latest'
    workers_ui_port: int = 5000
    default_timeout: int = 30
    docker_operations: Optional[DockerOperations] = dataclasses.field(default=None, metadata={"pickle_ignore": True})

    def __post_init__(self):
        # ensure our brokers are started
        import idmtools_platform_local.workers.brokers
        if self.docker_operations is None:
            # extract configuration details for the docker manager
            local_docker_options = [f.name for f in dataclasses.fields(DockerOperations)]
            opts = {k: v for k, v in self.__dict__.items() if k in local_docker_options}
            self.docker_operations = DockerOperations(**opts)
            self.docker_operations.create_services()

    """
    Represents the platform allowing to run simulations locally.
    """

    def retrieve_experiment(self, experiment_id):
        pass

    def get_assets_for_simulation(self, simulation, output_files):
        raise NotImplementedError("Not implemented yet in the LocalPlatform")

    def restore_simulations(self, experiment):
        raise NotImplementedError("Not implemented yet in the LocalPlatform")

    def refresh_experiment_status(self, experiment: 'TExperiment'):  # noqa: F821
        """

        Args:
            experiment:

        Returns:

        """
        # TODO Cleanup Client to return experiment id status directly
        status = SimulationsClient.get_all(experiment_id=experiment.uid)
        for s in experiment.simulations:
            sim_status = [st for st in status if st['simulation_uid'] == s.uid]

            if sim_status:
                s.status = local_status_to_common(sim_status[0]['status'])

    def create_experiment(self, experiment: IExperiment):
        from idmtools_platform_local.tasks.create_experiement import CreateExperimentTask

        m = CreateExperimentTask.send(experiment.tags, experiment.simulation_type)
        eid = m.get_result(block=True, timeout=self.default_timeout*1000)
        experiment.uid = eid
        path = os.path.join("/data", experiment.uid, "Assets")
        self.create_dir(path)
        self.send_assets_for_experiment(experiment)

    def send_assets_for_experiment(self, experiment):
        # Go through all the assets
        path = os.path.join("/data", experiment.uid, "Assets")
        list(map(functools.partial(self.send_asset_to_docker, path=path), experiment.assets))

    def send_assets_for_simulation(self, simulation):
        # Go through all the assets
        path = os.path.join("/data", simulation.experiment.uid, simulation.uid)
        list(map(functools.partial(self.send_asset_to_docker, path=path), simulation.assets))

    def send_asset_to_docker(self, asset: Asset, path:str):
        """

        Args:
            asset:
            path:

        Returns:

        """
        file_path = asset.absolute_path
        remote_path = os.path.join(path, asset.relative_path) if asset.relative_path else path
        result = self.create_dir(remote_path)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Creating directory {remote_path} result: {str(result)}")
        if not file_path:
            # Write file to temporary file from content
            if asset.content is None:
                raise IOError("Cannot determine the source of the assets. The Local Platform requires either the "
                              "absolute path or content to be set on the Asset object")
            with tempfile.NamedTemporaryFile(mode='wb') as tmpfile:
                tmpfile.write(asset.content)
                tmpfile.flush()

                self.docker_operations.copy_to_container(self.docker_operations.get_workers(), tmpfile.name,
                                                         remote_path, dest_name=asset.filename)
        else:
             self.docker_operations.copy_to_container(self.docker_operations.get_workers(), file_path,
                                                     remote_path)

    def create_dir(self, dir):
        worker = self.docker_operations.get_workers()
        user_str = self.docker_operations.system_info.user_group_str
        if not user_str: # on windows, use default user
            user_str = "1000:1000"
        return worker.exec_run(f'mkdir -p "{dir}"', user=user_str)

    def create_simulations(self, simulations_batch):
        from idmtools_platform_local.tasks.create_simulation import CreateSimulationTask

        ids = []
        for simulation in simulations_batch:
            m = CreateSimulationTask.send(simulation.experiment.uid, simulation.tags)
            sid = m.get_result(block=True, timeout=self.default_timeout*1000)
            simulation.uid = sid
            self.send_assets_for_simulation(simulation)
            ids.append(sid)
        return ids

    def run_simulations(self, experiment: IExperiment):
        from idmtools_platform_local.tasks.run import RunTask
        for simulation in experiment.simulations:
            RunTask.send(simulation.experiment.command.cmd, simulation.experiment.uid, simulation.uid)
