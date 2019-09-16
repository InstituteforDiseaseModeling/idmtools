import dataclasses
import functools
import logging
import os
from logging import getLogger
from typing import Optional, NoReturn
from dataclasses import dataclass
from pathlib import Path
from idmtools.assets import Asset
from idmtools.entities import IExperiment, IPlatform
# we have to import brokers so that the proper configuration is achieved for redis
from idmtools_platform_local.client.experiments_client import ExperimentsClient
from idmtools_platform_local.client.simulations_client import SimulationsClient
from idmtools_platform_local.docker.DockerOperations import DockerOperations
from idmtools_platform_local.workers.brokers import setup_broker
from idmtools.core.ExperimentFactory import experiment_factory

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
    host_data_directory: str = os.path.join(str(Path.home()), '.local_data')
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
    workers_image: str = 'idm-docker-staging.packages.idmod.org/idmtools_local_workers:0.2.0'
    workers_ui_port: int = 5000
    default_timeout: int = 30
    run_as: Optional[str] = None
    # We use this to manage our docker containers
    _docker_operations: Optional[DockerOperations] = dataclasses.field(default=None, metadata={"pickle_ignore": True})

    def __post_init__(self):
        super().__post_init__()
        # ensure our brokers are started
        setup_broker()
        if self._docker_operations is None:
            # extract configuration details for the docker manager
            local_docker_options = [f.name for f in dataclasses.fields(DockerOperations)]
            opts = {k: v for k, v in self.__dict__.items() if k in local_docker_options}
            self._docker_operations = DockerOperations(**opts)
            # start the services
            self._docker_operations.create_services()

    """
    Represents the platform allowing to run simulations locally.
    """

    def retrieve_experiment(self, experiment_id: str) -> 'IExperiment':
        """
        Restore experiment from local platform

        Args:
            experiment_id: Id of experiment to restore

        Returns:

        """
        experiment_dict = ExperimentsClient.get_one(experiment_id)
        experiment = experiment_factory.create(experiment_dict['tags'].get("type"), tags=experiment_dict['tags'])
        experiment.uid = experiment_dict['experiment_id']
        return experiment

    def get_assets_for_simulation(self, simulation: 'TSimulation', output_files):  # noqa: F821
        all_paths = set(output_files)

        assets = set(path for path in all_paths if path.lower().startswith("assets"))
        transients = all_paths.difference(assets)

        # Create the return dict
        ret = {}

        # Retrieve the transient if any
        if transients:
            sim_path = f'{simulation.experiment.uid}/{simulation.uid}'
            transients_files = self.retrieve_output_files(job_id_path=sim_path, paths=transients)
            ret = dict(zip(transients, transients_files))

        # Take care of the assets
        if assets:
            asset_path = f'{simulation.experiment.uid}'
            common_files = self.retrieve_output_files(job_id_path=asset_path, paths=assets)
            ret.update(dict(zip(assets, common_files)))

        return ret

    def restore_simulations(self, experiment: 'TExperiment'):  # noqa: F821
        simulation_dict = SimulationsClient.get_all(experiment_id=experiment.uid)

        for sim_info in simulation_dict:
            sim = experiment.simulation()
            sim.uid = sim_info['simulation_uid']
            sim.tags = sim_info['tags']
            sim.status = local_status_to_common(sim_info['status'])
            experiment.simulations.append(sim)

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
        eid = m.get_result(block=True, timeout=self.default_timeout * 1000)
        experiment.uid = eid
        path = "/".join(["/data", experiment.uid, "Assets"])
        self._docker_operations.create_directory(path)
        self.send_assets_for_experiment(experiment)

    def send_assets_for_experiment(self, experiment):
        # Go through all the assets
        path = "/".join(["/data", experiment.uid, "Assets"])
        list(map(functools.partial(self.send_asset_to_docker, path=path), experiment.assets))

    def send_assets_for_simulation(self, simulation):
        # Go through all the assets
        path = "/".join(["/data", simulation.experiment.uid, simulation.uid])
        list(map(functools.partial(self.send_asset_to_docker, path=path), simulation.assets))

    def send_asset_to_docker(self, asset: Asset, path: str) -> NoReturn:
        """
        Handles sending an asset to docker.

        Args:
            asset: Asset object to send
            path: Path to send find to within docker container

        Returns:
            (NoReturn): Nada
        """
        file_path = asset.absolute_path
        remote_path = "/".join([path, asset.relative_path]) if asset.relative_path else path
        # ensure remote directory exists
        result = self._docker_operations.create_directory(remote_path)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Creating directory {remote_path} result: {str(result)}")
        # is it a real file?
        worker = self._docker_operations.get_workers()
        self._docker_operations.copy_to_container(worker, file_path if file_path else asset.content, remote_path,
                                                  asset.filename if not file_path else None)

    def create_simulations(self, simulations_batch):
        from idmtools_platform_local.tasks.create_simulation import CreateSimulationTask

        ids = []
        for simulation in simulations_batch:
            m = CreateSimulationTask.send(simulation.experiment.uid, simulation.tags)
            sid = m.get_result(block=True, timeout=self.default_timeout * 1000)
            simulation.uid = sid
            self.send_assets_for_simulation(simulation)
            ids.append(sid)
        return ids

    def run_simulations(self, experiment: IExperiment):
        from idmtools_platform_local.tasks.run import RunTask
        for simulation in experiment.simulations:
            RunTask.send(simulation.experiment.command.cmd, simulation.experiment.uid, simulation.uid)

    def retrieve_output_files(self, job_id_path, paths):
        """
        Retrieves output files
        Args:
            job_id_path: For experiments, this should just be the id. For simulations, the path should be
            experiment_id/simulation id
            paths:

        Returns:

        """

        byte_arrs = []

        for path in paths:
            full_path = os.path.join(self.host_data_directory, 'workers', job_id_path, path)
            with open(full_path, 'rb') as fin:
                byte_arrs.append(fin.read())
        return byte_arrs
