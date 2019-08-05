import os
import platform
import shutil
import tarfile
import time
from dataclasses import dataclass
from io import BytesIO
from logging import getLogger
from typing import Optional, Union

import docker
from docker.models.containers import Container

from idmtools.core.SystemInformation import get_system_information
from idmtools_platform_local import __version__

logger = getLogger(__name__)


@dataclass
class DockerOperations:
    host_data_directory: str = os.path.join(os.getcwd(), '.local_data')
    network: str = 'idmtools'
    redis_image: str = 'redis:5.0.4-alpine'
    redis_port: int = 6379
    runtime: Optional[str] = 'runc'
    redis_mem_limit: str = '128m'
    redis_mem_reservation: str = '64m'
    postgres_image: str = 'postgres:11.4'
    postgres_mem_limit: str = '64m'
    postgres_mem_reservation: str = '32m'
    postgres_port: Optional[str] = 5432
    workers_image: str = 'idm-docker-production.packages.idmod.org/idmtools_local_workers:latest'
    workers_ui_port: int = 5000

    def __post_init__(self):
        if not os.path.exists(self.host_data_directory):
            os.makedirs(self.host_data_directory)
        self.timeout = 1
        self.system_info = get_system_information()
        self.client = docker.from_env()
        self.create_services()

    def create_services(self):

        self.get_network()
        self.get_redis()
        self.get_postgres()
        self.get_workers()

    def stop_services(self):
        for service in ['redis', 'postgres', 'workers']:
            container = getattr(self, f'get_{service}')()
            if container:
                name = container.name
                logger.debug(f'Stopping container {name}')
                container.stop()
                logger.debug(f'Removing container {name}')
                container.remove()

    def cleanup(self):
        self.stop_services()
        try:
            shutil.rmtree(self.host_data_directory, True)
        except PermissionError:
            logger.warning(f"Cannot cleanup directory {self.host_data_directory} because it is still in use")
            pass
        postgres_volume = self.client.volumes.list(filters=dict(name='idmtools_local_postgres'))
        if postgres_volume:
            postgres_volume[0].remove(True)

        network = self.get_network()
        if network:
            network.remove()

    def get_network(self):
        # check that the network exists
        network = self.client.networks.list([self.network])
        if not network:
            logger.debug(f'Creating network {self.network}')
            network = self.client.networks.create(self.network, driver='bridge', internal=False,
                                                          attachable=False, ingress=False, scope='local')
        else:
            network = network[0]
        return network

    def get_workers(self) -> str:
        logger.debug('Ensuring worker is running')
        workers_container = self.client.containers.list(filters=dict(name='idmtools_worker'))
        if not workers_container:
            container_config = self.create_worker_config()
            logger.debug(f'Worker Container Config {str(container_config)}')
            workers_container = self.client.containers.run(**container_config)
        else:
            workers_container = workers_container[0]
        return workers_container

    def create_worker_config(self):
        logger.debug(f'Creating working container')
        data_dir = os.path.join(self.host_data_directory, 'workers')
        os.makedirs(data_dir, exist_ok=True)
        docker_socket = '/var/run/docker.sock'
        if os.name == 'nt':
            docker_socket = '/' + docker_socket
        worker_volumes = {
            data_dir: dict(bind='/data', mode='rw'),
            docker_socket: dict(bind='/var/run/docker.sock', mode='rw')
        }
        environment = ['REDIS_URL=redis://redis:6379']
        if platform.system() in ["Linux", "Darwin"]:
            environment.append(f'CURRENT_UID={self.system_info.user_group_str}')
        port_bindings = self._get_optional_port_bindings(self.workers_ui_port, 5000)
        container_config = dict(name='idmtools_workers', hostname='idmtools',
                                image=self.workers_image, ports=port_bindings,
                                links=dict(idmtools_redis='redis', idmtools_postgres='postgres'),
                                volumes=worker_volumes, runtime=self.runtime, environment=environment)
        container_config.update(
            self.get_common_config(
                mem_limit=self.redis_mem_limit, mem_reservation=self.redis_mem_reservation
            ))
        return container_config

    @staticmethod
    def get_common_config(mem_limit=None, mem_reservation=None):
        config = dict(restart_policy=dict(MaximumRetryCount=15, name='on-failure'), detach=True,
                      labels=dict(idmtools_version=__version__))
        if mem_limit:
            config['mem_limit'] = mem_limit
        if mem_reservation:
            config['mem_reservation'] = mem_reservation
        return config

    def get_redis(self) -> str:
        logger.debug('Ensuring redis is running')
        redis_container = self.client.containers.list(filters=dict(name='idmtools_redis'))
        if not redis_container:
            container_config = self.create_redis_config()
            logger.debug(f'Redis Container Config {str(container_config)}')
            redis_container = self.client.containers.run(**container_config)
        else:
            redis_container = redis_container[0]
        return redis_container

    def create_redis_config(self):
        data_dir = os.path.join(self.host_data_directory, 'redis-data')
        os.makedirs(data_dir, exist_ok=True)
        redis_volumes = {
            data_dir: dict(bind='/data', mode='rw')
        }
        port_bindings = self._get_optional_port_bindings(self.redis_port, 6379)
        container_config = dict(name='idmtools_redis', hostname='redis', image=self.redis_image, ports=port_bindings,
                                volumes=redis_volumes)
        if platform.system() in ["Linux", "Darwin"]:
            container_config['user'] = self.system_info.user_group_str
        container_config.update(self.get_common_config(mem_limit=self.redis_mem_limit,
                                                       mem_reservation=self.redis_mem_reservation))
        return container_config

    def get_postgres(self) -> str:
        logger.debug('Ensuring postgres is running')
        postgres_container = self.client.containers.list(filters=dict(name='idmtools_postgres'))
        if not postgres_container:
            container_config = self.create_postgres_config()
            logger.debug(f'Postgres Container Config {str(container_config)}')
            postgres_container = self.client.containers.run(**container_config)
        else:
            postgres_container = postgres_container[0]
        return postgres_container

    def create_postgres_config(self):
        postgres_volume = self.client.volumes.list(filters=dict(name='idmtools_local_postgres'))
        if not postgres_volume:
            self.client.volumes.create(name='idmtools_local_postgres')
        postgres_volumes = dict(
            idmtools_local_postgres=dict(bind='/var/lib/postgresql/data', mode='rw')
        )
        port_bindings = self._get_optional_port_bindings(self.postgres_port, 5432)
        container_config = dict(name='idmtools_postgres', image=self.postgres_image, ports=port_bindings,
                                volumes=postgres_volumes, hostname='postgres',
                                environment=['POSTGRES_USER=idmtools', 'POSTGRES_PASSWORD=idmtools'])
        container_config.update(
            self.get_common_config(
                mem_limit=self.postgres_mem_limit, mem_reservation=self.postgres_mem_reservation)
        )
        return container_config

    @staticmethod
    def _get_optional_port_bindings(src_port: Optional[Union[str, int]], dest_port: Optional[Union[str, int]]):
        return {src_port: dest_port} if src_port is not None else None

    def copy_to_container(self, container: Container, file, destination_path):
        logger.debug(f'Copying {file} to docker container {container.id}')
        with self.create_archive(file) as archive:
            return container.put_archive(path=destination_path, data=archive.read())

    @staticmethod
    def create_archive(file_to_copy):
        pw_tarstream = BytesIO()
        pw_tar = tarfile.TarFile(fileobj=pw_tarstream, mode='w')
        file_data = open(file_to_copy, 'rb').read()
        tarinfo = tarfile.TarInfo(name=os.path.basename(file_to_copy))
        tarinfo.size = len(file_data)
        tarinfo.mtime = time.time()
        # tarinfo.mode = 0600
        pw_tar.addfile(tarinfo, BytesIO(file_data))
        pw_tar.close()
        pw_tarstream.seek(0)
        return pw_tarstream
