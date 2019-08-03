import os
import tarfile
import time
from dataclasses import dataclass
from io import BytesIO
from typing import Optional, Union

import docker
from docker.utils import create_archive
from idmtools.core.SystemInformation import get_system_information


@dataclass
class LocalDockerManager:
    auto_remove: bool
    network: str
    redis_image: str
    redis_port: int
    runtime: Optional[str]
    redis_mem_limit: str
    redis_mem_reservation: str
    postgres_image: str
    postgres_mem_limit: str
    postgres_mem_reservation: str
    postgres_port: Optional[str]
    workers_image: str
    workers_ui_port: int

    def __post_init__(self):
        self.timeout = 1
        self.system_info = get_system_information()
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

    def get_workers(self) -> str:
        workers_container = self.client.containers(filters=dict(name='idmtools_worker'))
        if not workers_container:
            data_dir = os.path.join(self.system_info.get_data_directory(), 'workers')
            os.makedirs(data_dir, exist_ok=True)
            docker_socket = '/var/run/docker.sock'
            if os.name == 'nt':
                docker_socket = '/' + docker_socket
            worker_volumes = [
                f'{data_dir}:/data',
                f'{docker_socket}:/var/run/docker.sock'
            ]
            networking_config = self._build_network_config('workers')
            host_config = self.client.create_host_config(auto_remove=self.auto_remove, binds=worker_volumes,
                                                         restart_policy='always',
                                                         port_bindings={self.workers_ui_port: 5000}
                                                         )
            environment = ['REDIS_URL=redis://redis:6379']
            if self.system_info.get_user():
                environment.append(f'CURRENT_UID={self.system_info.get_user()}')
            workers_container = self.client.create_container(image=self.postgres_image, hostname='workers',
                                                             environment=environment, ports=[5000], detach=True,
                                                             host_config=host_config, volumes=['/data'],
                                                             runtime=self.runtime,
                                                             networking_config=networking_config,
                                                             name='idmtools_workers'
                                                             )
        else:
            workers_container = workers_container[0]
        return workers_container['Id']

    def get_redis(self) -> str:
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
        else:
            redis_container = redis_container[0]
        return redis_container['Id']

    def get_postgres(self) -> str:
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
        else:
            postgres_container = postgres_container[0]
        return postgres_container['Id']

    @staticmethod
    def _get_optional_port_bindings(src_port: Optional[Union[str, int]], dest_port: Optional[Union[str, int]]):
        return {src_port: dest_port} if src_port is not None else None

    def copy_to_container(self, container_id, artifact_file):
        with create_archive(artifact_file) as archive:
            self.client.put_archive(container=container_id, path='/tmp', data=archive)

    @staticmethod
    def create_archive(artifact_file):
        pw_tarstream = BytesIO()
        pw_tar = tarfile.TarFile(fileobj=pw_tarstream, mode='w')
        file_data = open(artifact_file, 'r').read()
        tarinfo = tarfile.TarInfo(name=artifact_file)
        tarinfo.size = len(file_data)
        tarinfo.mtime = time.time()
        # tarinfo.mode = 0600
        pw_tar.addfile(tarinfo, BytesIO(file_data))
        pw_tar.close()
        pw_tarstream.seek(0)
        return pw_tarstream
