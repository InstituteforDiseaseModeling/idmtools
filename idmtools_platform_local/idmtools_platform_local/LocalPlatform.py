import base64
import os
import platform
from abc import abstractmethod, ABC
from typing import Optional, Union

from dramatiq import group
from dataclasses import dataclass
from idmtools.core import EntityStatus
from idmtools.entities import IExperiment, IPlatform
# we have to import brokers so that the proper configuration is achieved for redis
from idmtools_platform_local.client.experiments_client import ExperimentsClient
from idmtools_platform_local.client.simulations_client import SimulationsClient
from idmtools_platform_local.tasks.create_assest_task import AddAssetTask
from idmtools_platform_local.tasks.create_experiement import CreateExperimentTask
from idmtools_platform_local.tasks.create_simulation import CreateSimulationTask
from idmtools_platform_local.tasks.run import RunTask
from pathlib import Path
import docker

status_translate = dict(
    created='CREATED',
    in_progress='RUNNING',
    canceled='canceled',
    failed='FAILED',
    done='SUCCEEDED'
)


def local_status_to_common(status):
    return EntityStatus[status_translate[status]]


class LocalSystemInformation(ABC):

    @staticmethod
    def get_data_directory() -> Optional[str]:
        return str(Path.home())

    @abstractmethod
    def get_user(self) -> Optional[str]:
        pass


class LinuxSystemInformation(LocalSystemInformation):

    def get_user(self) -> Optional[str]:
        """
        Returns a user/group string for executing docker containers as the correct user

        For example
        '1000:1000'
        Returns:
            (str): Container user id and group id of the current user
        """
        return f'{os.getuid()}:{os.getgid()}'


class WindowsSystemInformation(LocalSystemInformation):

    def get_user(self) -> Optional[str]:
        """
        On the windows platform, we don't need a user for docker

        Returns:
            (None): Returns none meaning there is no user id to pass along
        """
        return None


@dataclass
class LocalDockerManager:
    auto_remove: bool
    network: str
    redis_image: str
    redis_port: int
    runtime: str
    redis_mem_limit: str
    redis_mem_reservation: str
    postgres_image: str
    postgres_mem_limit: str
    postgres_mem_reservation: str
    postgres_port: Optional[str]
    workers_image: str
    local_ui_port: int

    def __post_init__(self):
        self.timeout = 1
        self.system_info = LinuxSystemInformation() if platform in ["linux", "linux2",
                                                                    "darwin"] else WindowsSystemInformation()
        self.client = docker.api.APIClient(timeout=self.timeout)
        self.get_network()
        self.get_redis()
        self.get_postgres()
        self.get_workers()

    def get_network(self):
        # check that the network exists
        network = self.client.networks([self.network])
        if not network:
            network = self.client.create_network(self.network, driver='bridge', internal=False, attachable=False,
                                                 ingress=False, scope='local')
        else:
            network = network[0]
        return network

    def _build_network_config(self, name):
        networking_config = self.client.create_networking_config({
            self.network: self.client.create_endpoint_config(
                aliases=[name, f'{name}.idmtools']
            )
        })
        return networking_config

    def get_workers(self):
        workers_container = self.client.containers(filters=dict(name='idmtools_worker'))
        if not workers_container:
            data_dir = os.path.join(self.system_info.get_data_directory(), 'workers')
            os.makedirs(data_dir, exist_ok=True)
            worker_volumes = [
                f'{data_dir}:/data'
            ]
            networking_config = self._build_network_config('workers')
            host_config = self.client.create_host_config(auto_remove=self.auto_remove, binds=worker_volumes,
                                                         restart_policy='always',
                                                         port_bindings={self.local_ui_port: 5000}
                                                         )
            environment = ['REDIS_URL=redis://redis:6379']
            if self.system_info.get_user():
                environment.append(f'CURRENT_UID={self.system_info.get_user()}')
            workers_container = self.client.create_container(image=self.postgres_image, hostname='workers',
                                                             environment=environment, ports=[5000], detach=True,
                                                             host_config=host_config, volumes=['/data'],
                                                             networking_config=networking_config,
                                                             name='idmtools_workers'
                                                             )
        return workers_container

    def get_redis(self):
        # ensure database is running
        redis_container = self.client.containers(filters=dict(name='idmtools_redis'))
        if not redis_container:
            data_dir = os.path.join(self.system_info.get_data_directory(), 'redis-data')
            os.makedirs(data_dir, exist_ok=True)
            redis_volumes = [
                f'{data_dir}:/data'
            ]
            networking_config = self._build_network_config('redis')
            port_bindings = self._get_optional_port_bindings(self.redis_port, 6379)
            host_config = self.client.create_host_config(auto_remove=self.auto_remove, mem_limit=self.redis_mem_limit,
                                                         mem_reservation=self.redis_mem_reservation,
                                                         binds=redis_volumes, port_bindings=port_bindings,
                                                         restart_policy='always',
                                                         )
            redis_container = self.client.create_container(image=self.redis_image, hostname='redis', ports=[6379],
                                                           user=self.system_info.get_user(), host_config=host_config,
                                                           networking_config=networking_config,
                                                           name='idmtools_redis', volumes=['/data'], detach=True)
        return redis_container

    def get_postgres(self):
        postgres_container = self.client.containers(filters=dict(name='idmtools_postgres'))
        if not postgres_container:
            postgres_volume = self.client.volumes(filters=dict(name='idmtools_local_postgres'))
            if not postgres_volume:
                self.client.create_volume(name='idmtools_local_postgres')
            postgres_volumes = [
                f'idmtools_local_postgres:/var/lib/postgresql/data'
            ]
            networking_config = self._build_network_config('postgres')
            port_bindings = self._get_optional_port_bindings(self.postgres_port, 5432)
            host_config = self.client.create_host_config(auto_remove=self.auto_remove,
                                                         mem_limit=self.postgres_mem_limit,
                                                         mem_reservation=self.postgres_mem_reservation,
                                                         restart_policy='always',
                                                         binds=postgres_volumes, port_bindings=port_bindings
                                                         )
            postgres_container = self.client.create_container(image=self.postgres_image, hostname='postgres',
                                                              environment=['POSTGRES_USER=idmtools',
                                                                           'POSTGRES_PASSWORD=idmtools'],
                                                              ports=[5432], host_config=host_config, volumes=['/data'],
                                                              detach=True, name='idmtools_postgres',
                                                              networking_config=networking_config)
        return postgres_container

    @staticmethod
    def _get_optional_port_bindings(src_port: Optional[Union[str, int]], dest_port:Optional[Union[str, int]]):
        return {src_port: dest_port} if src_port is not None else None


@dataclass
class LocalPlatform(IPlatform):
    auto_remove: bool = True
    network: str = 'idmtools'
    redis_image: str = 'redis:5.0.4-alpine'
    redis_port: int = 6379
    runtime: str = None
    redis_mem_limit: str = '128m'
    redis_mem_reservation: str = '64m'
    postgres_image: str = 'postgres:11.4'
    postgres_mem_limit: str = '64m'
    postgres_mem_reservation: str = '32m'
    postgres_port: Optional[str] = 5432
    workers_image: str = 'idm-docker-production.packages.idmod.org:latest'
    local_ui_port: int = 5000

    def __post_init__(self):
        dm = LocalDockerManager(**self.__dict__)



    """
    Represents the platform allowing to run simulations locally.
    """

    def retrieve_experiment(self, experiment_id):
        pass

    def get_assets_for_simulation(self, simulation, output_files):
        raise NotImplemented("Not implemented yet in the LocalPlatform")

    def restore_simulations(self, experiment):
        raise NotImplemented("Not implemented yet in the LocalPlatform")

    def refresh_experiment_status(self, experiment: 'TExperiment'):
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
        m = CreateExperimentTask.send(experiment.tags, experiment.simulation_type)
        eid = m.get_result(block=True)
        experiment.uid = eid
        self.send_assets_for_experiment(experiment)

    def send_assets_for_experiment(self, experiment):
        # Go through all the assets
        messages = []
        for asset in experiment.assets:
            # we are currently using queues to send our assets. This is not the greatest idea
            # For now, we will continue to do that until issues
            # https://github.com/InstituteforDiseaseModeling/idmtools/issues/254 is resolved
            messages.append(
                AddAssetTask.message(experiment.uid, asset.filename, path=asset.relative_path,
                                     contents=base64.b64encode(asset.content).decode('utf-8')))
        group(messages).run().wait()

    def send_assets_for_simulation(self, simulation):
        # Go through all the assets
        messages = []
        for asset in simulation.assets:
            messages.append(
                AddAssetTask.message(simulation.experiment.uid, asset.filename, path=asset.relative_path,
                                     contents=base64.b64encode(asset.content).decode('utf-8'),
                                     simulation_id=simulation.uid))
        group(messages).run().wait()

    def create_simulations(self, simulations_batch):
        ids = []
        for simulation in simulations_batch:
            m = CreateSimulationTask.send(simulation.experiment.uid, simulation.tags)
            sid = m.get_result(block=True)
            simulation.uid = sid
            self.send_assets_for_simulation(simulation)
            ids.append(sid)
        return ids

    def run_simulations(self, experiment: IExperiment):
        for simulation in experiment.simulations:
            RunTask.send(simulation.experiment.command.cmd, simulation.experiment.uid, simulation.uid)
