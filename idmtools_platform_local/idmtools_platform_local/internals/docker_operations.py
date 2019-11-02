import dataclasses
import io
import logging
import os
import shutil
import tarfile
import time
from concurrent.futures import as_completed
from concurrent.futures.thread import ThreadPoolExecutor
from dataclasses import dataclass
from io import BytesIO
from logging import getLogger
from pathlib import Path
from typing import BinaryIO, Dict, List, NoReturn, Optional, Tuple, Union
import docker
from docker.models.containers import Container
from docker.models.networks import Network
from idmtools.core.system_information import get_system_information
from idmtools.utils.decorators import optional_yaspin_load, ParallelizeDecorator
from idmtools_platform_local.internals.infrastructure.base_docker import BaseServiceContainer
from idmtools_platform_local.internals.infrastructure.postgres import PostgresContainer
from idmtools_platform_local.internals.infrastructure.redis import RedisContainer
from idmtools_platform_local.internals.infrastructure.workers import WorkersContainer

logger = getLogger(__name__)
# thread queue for docker copy operations
io_queue = ParallelizeDecorator()


# determine our default base directory. We almost always want to use the users home directory
# except odd environments like docker-in docker, special permissions, etc
default_base_sir = os.getenv('IDMTOOLS_DATA_BASE_DIR', str(Path.home()))
SERVICES = [PostgresContainer, RedisContainer, WorkersContainer]


@dataclass
class DockerOperations:
    host_data_directory: str = os.path.join(default_base_sir, '.local_data')
    network: str = 'idmtools'
    redis_image: str = 'redis:5.0.4-alpine'
    redis_port: int = 6379
    runtime: Optional[str] = 'runc'
    redis_mem_limit: str = '256m'
    redis_mem_reservation: str = '32m'
    postgres_image: str = 'postgres:11.4'
    postgres_mem_limit: str = '128m'
    postgres_mem_reservation: str = '32m'
    postgres_port: Optional[str] = 5432
    workers_image: str = None
    workers_ui_port: int = 5000
    workers_mem_limit: str = None
    workers_mem_reservation: str = '64m'
    run_as: Optional[str] = None
    _fileio_pool = ThreadPoolExecutor()

    _services: Dict = None

    def __post_init__(self):
        """
        Acts like our constructor after dataclasses has populated our fields. Currently we use it to initialize our
        docker client and get local system information
        Returns:

        """
        self._services = dict()
        # Make sure the host_data_dir exists
        os.makedirs(self.host_data_directory, exist_ok=True)

        self.timeout = 1
        self.system_info = get_system_information()
        if self.run_as is None:
            self.run_as = self.system_info.user_group_str

        if self.run_as == "0:0":
            message = "You cannot run the containers as the root user!. Please select another value for 'run_as'. "
            if self.system_info.user_group_str == "0:0":
                message += " It appears you executed a script/command as the local root user or use sudo to start the" \
                           " Local Platform. If that is the case, use the 'run_as' configuration option in your " \
                           "idmtools.ini Local Platform configuration block or initializing the Local Platform object"
            raise ValueError(message)
        self.client = docker.from_env()
        self.init_services()

    @optional_yaspin_load(text="Ensure IDM Tools Local Platform services are loaded")
    def create_services(self, spinner=None) -> NoReturn:
        """
        Create all the components of our

        Our architecture is as depicted in the UML diagram below

        .. uml::

            @startuml
            database "Postgres Container" as db
            node "Redis Container"as redis
            node "Workers Container" {
                [UI] -> db
                rectangle "Python Workers" {
                    rectangle "Worker ..." as w2
                    rectangle "Worker 1" as w1
                    w1 <---> db : Get/Update Status
                    w1 <---> redis : Get task/Add Task
                    w2 <---> db
                    w2 <---> redis
                }
            }
            file "User Python Script" as u
            u ...> redis : Submit task
            u <... redis : Get result
            @enduml

        Returns:
            (NoReturn)
        """
        try:
            self.get_network()
            for i, service in enumerate(SERVICES):
                sn = service.__name__
                # wait on services to be ready for workers
                if sn == 'WorkersContainer':
                    retries = 0
                    while retries < 5:
                        time.sleep(0.2)
                        if self.is_port_open('127.0.0.1', self.postgres_port) and \
                            self.is_port_open('127.0.0.1', self.redis_port):
                            break
                        retries += 1
                    if retries > 4:
                        logger.warning("Possible issue with Postgres/Redis. Could not connect to server ports")
                self._services[sn].get_or_create(spinner)
        except Exception as e:
            if logger.isEnabledFor(logging.DEBUG):
                logger.exception(e)
            raise e

    @staticmethod
    def is_port_open(host, port):
        import socket
        from contextlib import closing
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            if isinstance(port, int) and sock.connect_ex((host, port)) == 0:
                return True
            else:
                return False

    def init_services(self):
        for i, service in enumerate(SERVICES):
            sn = service.__name__
            if sn not in self._services:
                self._services[sn] = service(**self.get_container_config(service))

    @optional_yaspin_load(text="Restarting IDM-Tools services")
    def restart_all(self, spinner=None) -> NoReturn:
        """
        Restart all the services IDM-Tools services

        Returns:
            (NoReturn)
        """

        for service in self._services.values():
            service.restart()

    @optional_yaspin_load(text="Stopping IDM Tools Local Platform services")
    def stop_services(self, spinner=None) -> NoReturn:
        """
        Stops all running IDM Tools services

        Returns:
            (NoReturn)
        """
        with ThreadPoolExecutor() as pool:
            futures = []
            for service in self._services.values():
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f'Stopping {service.__class__.__name__}')
                pool.submit(self.stop_service_and_wait, service)
            for done in as_completed(futures):
                pass

    @staticmethod
    def stop_service_and_wait(service):
        service.stop(True)
        container = service.get()
        while container:
            time.sleep(0.1)
            container = service.get()
        return True

    def delete_files_below_level(self, directory, target_level=1, current_level=1):
        for fn in os.listdir(directory):
            file_path = os.path.join(directory, fn)
            try:
                # we only delete items at the target level
                if os.path.isfile(file_path) and target_level == current_level:
                    logger.debug(f"Deleting {file_path}")
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    # if this is target level, let's delete it
                    if target_level == current_level:
                        logger.debug(f"Deleting {file_path}")
                        shutil.rmtree(file_path)
                    else:
                        clevel = current_level + 1 if current_level > 1 else 1
                        self.delete_files_below_level(file_path, target_level, clevel)
            except PermissionError as e:
                if logger.isEnabledFor(logging.DEBUG):
                    logger.exception(e)
                pass

    def cleanup(self, delete_data: bool = True, shallow_delete: bool = True, tear_down_broker = False) -> NoReturn:
        """
        Stops the running services, removes local data, and removes network. You can optionally disable the deleting
        of local data

        Args:
            delete_data(bool): When true, deletes local data
            shallow_delete(bool): Deletes the data but not the container folders(redis, workers). Preferred to preserve
                permissions and resolve docker issues

        Returns:
            (NoReturn)
        """
        self.stop_services()

        if tear_down_broker:
            from idmtools_platform_local.internals.workers.brokers import close_brokers
            logger.debug("Closing brokers down")
            close_brokers()

        try:
            if delete_data and not shallow_delete:
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f"Deleting local platform data at: {self.host_data_directory}")
                shutil.rmtree(self.host_data_directory, True)
            elif delete_data and shallow_delete:
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f"Shallow deleting: {self.host_data_directory}")
                self.delete_files_below_level(self.host_data_directory, 3)
        except PermissionError:
            print(f"Cannot cleanup directory {self.host_data_directory} because it is still in use")
            logger.warning(f"Cannot cleanup directory {self.host_data_directory} because it is still in use")
            pass
        if delete_data:
            postgres_volume = self.client.volumes.list(filters=dict(name='idmtools_local_postgres'))
            if postgres_volume:
                postgres_volume[0].remove(True)

        # TODO Check when items have been deleted

        network = self.get_network()
        if network:
            logger.debug(f'Removing docker network: {self.network}')
            network.remove()

    def get_network(self) -> Network:
        """
        Fetches the IDM Tools network

        Returns:
            (Network) Return Docker network object
        """
        # check that the network exists
        network = self.client.networks.list([self.network])
        if not network:
            logger.debug(f'Creating network {self.network}')
            network = self.client.networks.create(self.network, driver='bridge', internal=False,
                                                  attachable=False, ingress=False, scope='local')
        else:
            network = network[0]
        return network

    @io_queue.parallelize
    def copy_to_container(self, container: Container, file: Union[str, bytes], destination_path: str,
                          dest_name: Optional[str] = None) -> bool:
        """
        Copies a physical file to a container. You can also choose a different name for the destination file by using
        the dest_name option

        Args:
            container: Container to copy the file to
            file:  Path to the file to copy
            destination_path: Path within the container to copy the file to(should be a directory)
            dest_name: Optional parameter for destination filename. By default the source filename is used

        Returns:
            (bool) True if the copy succeeds, False otherwise
        """
        if isinstance(file, bytes):
            file = BytesIO(file)
        if type(file) is str:
            logger.debug(f'Copying {file} to docker container {container.id}:{destination_path}')
            name = dest_name if dest_name else os.path.basename(file)
            target_file = os.path.join(self.host_data_directory,
                                       destination_path.replace('/data', '/workers')[1:], name)

            # Make sure to have the correct separators for the path
            target_file = target_file.replace('/', os.sep).replace('\\', os.sep)

            # Do the copy
            shutil.copy(file, target_file)
            return True
        elif isinstance(file, BytesIO):
            target_file = os.path.join(self.host_data_directory, destination_path.replace('/data', '/workers')[1:],
                                       dest_name)
            # Make sure to have the correct separators for the path
            target_file = target_file.replace('/', os.sep).replace('\\', os.sep)

            logger.debug(f'Copying {dest_name} to docker container {container.id}:{destination_path} '
                         f'through {target_file}')

            with open(target_file, 'wb') as of:
                of.write(file.read())
            return True

    def sync_copy(self, futures):
        """
        Sync the copy operations queue in the io_queue. This allows us to take advantage of multi-threaded copying
            while also making it convenient to have sync points, such as uploading the assets in parallel but pausing
            just before sync point

        Args:
            futures:

        Returns:

        """
        if not isinstance(futures, list):
            futures = [futures]
        return io_queue.get_results(futures)

    def copy_multiple_to_container(self, container: Container,
                                   files: Dict[str, List[Tuple[Union[str, bytes], Optional[str]]]],
                                   join_on_copy: bool = True):
        results = []
        for dest_path, sub_files in files.items():
            for fn in sub_files:
                results.append(self.copy_to_container(container, fn[0], dest_path, fn[1]))

        if join_on_copy:
            return all(io_queue.get_results(results))
        # If we don't join, we assume the copy succeeds for now. This really means somewhere else should be handling the
        # data join for this
        return True

    @staticmethod
    def create_archive_from_bytes(content: Union[bytes, BytesIO, BinaryIO], name: str) -> BytesIO:
        """
        Create a tar archive from bytes. Used to copy to docker

        Args:
            content: Content to copy into tar
            name: Name for file in archive

        Returns:
            (BytesIO) Return bytesIO object
        """
        if type(content) is bytes:
            content = BytesIO(content)
        content.seek(0, io.SEEK_END)
        file_length = content.tell()
        content.seek(0)
        pw_tarstream = BytesIO()
        pw_tar = tarfile.TarFile(fileobj=pw_tarstream, mode='w')
        tarinfo = tarfile.TarInfo(name=name)
        tarinfo.size = file_length
        tarinfo.mtime = time.time()
        # tarinfo.mode = 0600
        pw_tar.addfile(tarinfo, content)
        pw_tar.close()
        pw_tarstream.seek(0)
        return pw_tarstream

    def create_directory(self, dir: str) -> bool:
        """
        Create a directory in a container

        Args:
            dir: Path to directory to create
            container: Container to create directory in. Default to worker container

        Returns:
            (ExecResult) Result of the mkdir operation
        """
        path = os.path.join(self.host_data_directory, dir.replace('/data', '/workers')[1:])
        path.replace('/', os.sep).replace('\\', os.sep)
        os.makedirs(path, exist_ok=True)
        return True

    def get_container_config(self, service: BaseServiceContainer):
        fields = {f.name: f for f in dataclasses.fields(service)}
        my_fields = dataclasses.fields(self)

        prefix = fields['config_prefix'].default

        opts = dict(client=self.client)
        for field in my_fields:
            dest_name = field.name.replace(prefix, "")
            if dest_name in fields and getattr(self, field.name, None) is not None:
                opts[dest_name] = getattr(self, field.name)

        return opts
