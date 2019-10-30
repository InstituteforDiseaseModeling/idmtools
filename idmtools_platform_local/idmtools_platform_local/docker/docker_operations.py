import io
import logging
import os
import platform
import shutil
import tarfile
import time
from concurrent.futures.thread import ThreadPoolExecutor
from dataclasses import dataclass
from getpass import getpass
from io import BytesIO
from logging import getLogger
from pathlib import Path
from typing import BinaryIO, Dict, List, NoReturn, Optional, Tuple, Union

import docker
from docker.errors import APIError
from docker.models.containers import Container
from docker.models.networks import Network

from idmtools.core.system_information import get_system_information
from idmtools.utils.decorators import optional_yaspin_load, ParallelizeDecorator
from idmtools_platform_local import __version__

logger = getLogger(__name__)
# thread queue for docker copy operations
io_queue = ParallelizeDecorator()

# determine default docker to use
# we first check if it is nightly. Nightly will ALWAYS use staging
if "nightly" in __version__:
    docker_repo = 'idm-docker-staging.packages.idmod.org'
# otherwise we let the user have come control by default to docker-public
else:
    docker_repo = f'{os.getenv("DOCKER_REPO", "idm-docker-public")}.packages.idmod.org'

if logger.isEnabledFor(logging.DEBUG):
    logger.debug(f"Default docker repo set to: {docker_repo}")

default_image = f'{docker_repo}/idmtools_local_workers:{__version__.replace("+", ".")}'
# determine our default base directory. We almost always want to use the users home directory
# except odd environments like docker-in docker, special permissions, etc
default_base_sir = os.getenv('IDMTOOLS_DATA_BASE_DIR', str(Path.home()))


@dataclass
class DockerOperations:
    host_data_directory: str = os.path.join(default_base_sir, '.local_data')
    network: str = 'idmtools'
    redis_image: str = 'redis:5.0.4-alpine'
    redis_port: int = 6379
    runtime: Optional[str] = 'runc'
    redis_mem_limit: str = '128m'
    redis_mem_reservation: str = '64m'
    workers_mem_limit: str = '512m'
    workers_mem_reservation: str = '128m'
    postgres_image: str = 'postgres:11.4'
    postgres_mem_limit: str = '64m'
    postgres_mem_reservation: str = '32m'
    postgres_port: Optional[str] = 5432
    workers_image: str = default_image
    workers_ui_port: int = 5000
    run_as: Optional[str] = None
    _fileio_pool = ThreadPoolExecutor()

    def __post_init__(self):
        """
        Acts like our constructor after dataclasses has populated our fields. Currently we use it to initialize our
        docker client and get local system information
        Returns:

        """
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
            self.get_redis()
            self.get_postgres()
        except Exception as e:
            if logger.isEnabledFor(logging.DEBUG):
                logger.exception(e)
            raise e
        # wait on services to start
        # in the future this could be improved with service detection
        time.sleep(5)

        retries = 0
        while retries < 3:
            try:
                self.get_workers()
                logger.debug("services started. waiting for platform to become ready")
            except APIError as e:
                if logger.isEnabledFor(logging.DEBUG):
                    logger.exception(e)
                if e.status_code in [500]:
                    content = e.response.json()
                    if 'message' in content and 'unauthorized' in content['message']:
                        if spinner:
                            spinner.hide()
                        registry = self.workers_image.split("/")[0]
                        print(f"\nAuthentication needed for {registry}.\nIt is best to login manually outside of "
                              f"idmtools using\n docker login {registry}\nas this will save your password\n"
                              f"Prompting for credentials for one time user:\n")
                        username = input(f'{registry} Username:')
                        password = getpass('Password:')
                        self.client.login(username, password, registry=registry)
                        retries += 1
                        if spinner:
                            spinner.show()
                elif e.status_code == 404:
                    print(f'\n\nCould not locate a docker image with the tag: {self.workers_image}\n'
                          f'Please check the name of the image or ensure you have built that image locally.'
                          f'You can test a manual pull using \n'
                          f'docker pull {self.workers_image}')
                    logger.exception(e)
                    retries += 1
                    raise
                else:
                    logger.exception(e)
                    retries += 1
                    raise
        if retries > 2:
            raise ValueError("Could not run workers image. Likely causes are:\n\t- A used port"
                             "\n\t-A service being down such as redis or postgres"
                             "\n\t-Authentication issues with the docker registry")
        time.sleep(5)

    @optional_yaspin_load(text="Restarting IDM-Tools services")
    def restart_all(self, spinner=None) -> NoReturn:
        """
        Restart all the services IDM-Tools services

        Returns:
            (NoReturn)
        """

        redis = self.get_redis()
        if redis:
            redis.restart()

        postgres = self.get_postgres()
        if postgres:
            postgres.restart()

        workers = self.get_workers()
        if workers:
            workers.restart()

    @optional_yaspin_load(text="Stopping IDM Tools Local Platform services")
    def stop_services(self, spinner=None) -> NoReturn:
        """
        Stops all running IDM Tools services

        Returns:
            (NoReturn)
        """
        for service in ['redis', 'postgres', 'workers']:
            container = getattr(self, f'get_{service}')(False)
            if container:
                name = container.name
                logger.debug(f'Stopping container {name}')
                container.stop()
                logger.debug(f'Removing container {name}')
                container.remove()

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

    def cleanup(self, delete_data: bool = True, shallow_delete: bool = True) -> NoReturn:
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
        try:
            if delete_data and not shallow_delete:
                shutil.rmtree(self.host_data_directory, True)
            elif delete_data and shallow_delete:
                self.delete_files_below_level(self.host_data_directory, 3)
        except PermissionError:
            print(f"Cannot cleanup directory {self.host_data_directory} because it is still in use")
            logger.warning(f"Cannot cleanup directory {self.host_data_directory} because it is still in use")
            pass
        if delete_data:
            postgres_volume = self.client.volumes.list(filters=dict(name='idmtools_local_postgres'))
            if postgres_volume:
                postgres_volume[0].remove(True)

        network = self.get_network()
        if network:
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

    def get_workers(self, create: bool = True) -> Optional[Container]:
        """
        Gets the workers container

        Args:
            create: When set to true, container is created if it is not found

        Returns:
            (Optional[Container]): A Container object is always returned When used with *create=True*. It is possible
            that *None* is returned when *create=False*
        """
        logger.debug('Checking if worker is running')
        try:
            workers_container = self.client.containers.list(filters=dict(name='idmtools_worker'), all=True)
            if not workers_container and create:
                container_config = self.create_worker_config()
                logger.debug(f'Worker Container Config {str(container_config)}')
                workers_container = self.client.containers.run(**container_config)
            elif type(workers_container) is list and len(workers_container):
                workers_container = workers_container[0]
                if create:
                    workers_container = self.ensure_container_running(workers_container)
            return workers_container
        except APIError as e:
            if logger.isEnabledFor(logging.DEBUG):
                logger.exception(e)
            if 'address already in use' in e.response:
                raise EnvironmentError(f"Port {self.workers_ui_port} already in use. Please configure another port or "
                                       f"stop the service/application using port {self.workers_ui_port}"
                                       f"for the Local Platform UI") from e
            else:  # we don't know what the issue is so kick it down the road
                raise e

    @staticmethod
    def ensure_container_running(container: Container) -> Container:
        """
        Ensures the container is running. If not, it will be started

        Args:
            container(Container):  Container to check if running
        Returns:

        """
        if container.status in ['exited', 'created']:
            logger.debug(f"Restarting container: {container.name}")
            container.start()
            container.reload()
        return container

    def create_worker_config(self) -> dict:
        """
        Returns the docker config for the workers container

        Returns:
            (dict) Dictionary representing the docker config for the workers container
        """
        logger.debug(f'Creating working container')
        default_data_host_dir = os.getenv("IDMTOOLS_WORKER_DATA_MOUNT_BY_VOLUMENAME", None)
        if not default_data_host_dir:
            data_dir = os.path.join(self.host_data_directory, 'workers')
            os.makedirs(data_dir, exist_ok=True)
        else:
            logger.debug(f"Specifying Data directory using named volume {default_data_host_dir}")
            data_dir = f'{default_data_host_dir}'
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Worker default directory is {data_dir}")

        docker_socket = '/var/run/docker.sock'
        if os.name == 'nt':
            docker_socket = '/' + docker_socket
        worker_volumes = {
            data_dir: dict(bind='/data', mode='rw'),
            docker_socket: dict(bind='/var/run/docker.sock', mode='rw')
        }
        environment = [f'REDIS_URL=redis://redis:{self.redis_port}',
                       f'HOST_DATA_PATH={data_dir}',
                       f'SQLALCHEMY_DATABASE_URI='
                       f'postgresql+psycopg2://idmtools:idmtools@postgres:{self.postgres_port}/idmtools']
        if platform.system() in ["Linux", "Darwin"]:
            environment.append(f'CURRENT_UID={self.run_as}')
        port_bindings = self._get_optional_port_bindings(self.workers_ui_port, 5000)
        container_config = dict(name='idmtools_workers', hostname='idmtools',
                                image=self.workers_image, ports=port_bindings,
                                links=dict(idmtools_redis='redis', idmtools_postgres='postgres'),
                                volumes=worker_volumes, runtime=self.runtime, environment=environment)

        container_config.update(
            self.get_common_config(mem_limit=self.workers_mem_limit, mem_reservation=self.workers_mem_reservation)
        )

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Worker Config: {container_config}")
        return container_config

    @staticmethod
    def get_common_config(mem_limit: Optional[str] = None, mem_reservation: Optional[str] = None) -> dict:
        """
        Returns portions of docker container configs that are common between all the different containers used within
        our platform

        Args:
            mem_limit (Optional[str]): Limit memory
            mem_reservation (Optional[str]): Reserve memory

        Returns:

        Notes:
            Memory strings should match those used by docker. See --memory details at
            https://docs.docker.com/engine/reference/run/#runtime-constraints-on-resources
        """
        config = dict(restart_policy=dict(MaximumRetryCount=15, name='on-failure'), detach=True,
                      labels=dict(idmtools_version=__version__))
        if mem_limit:
            config['mem_limit'] = mem_limit
        if mem_reservation:
            config['mem_reservation'] = mem_reservation
        return config

    def get_redis(self, create=True) -> Container:
        """
        Gets the redis container

        Args:
            create: When set to true, container is created if it is not found

        Returns:
            (Optional[Container]): A Container object is always returned When used with *create=True*. It is possible
            that *None* is returned when *create=False*
        """
        logger.debug('Checking if redis is running')
        redis_container = self.client.containers.list(filters=dict(name='idmtools_redis'), all=True)
        if not redis_container and create:
            container_config = self.create_redis_config()
            logger.debug(f'Redis Container Config {str(container_config)}')
            redis_container = self.client.containers.run(**container_config)
        elif type(redis_container) is list and len(redis_container):
            redis_container = redis_container[0]
            if create:
                redis_container = self.ensure_container_running(redis_container)
        return redis_container

    def create_redis_config(self):
        """
        Returns the docker config for the redis container

        Returns:
            (dict) Dictionary representing the docker config for the redis container
        """
        default_data_host_dir = os.getenv("IDMTOOLS_REDIS_DATA_MOUNT_BY_VOLUMENAME", None)
        if not default_data_host_dir:
            data_dir = os.path.join(self.host_data_directory, 'redis-data')
            os.makedirs(data_dir, exist_ok=True)
        else:
            logger.debug(f"Specifying Data directory using named volume {default_data_host_dir}")
            data_dir = f'{default_data_host_dir}'
        os.makedirs(data_dir, exist_ok=True)
        redis_volumes = {
            data_dir: dict(bind='/data', mode='rw')
        }
        port_bindings = self._get_optional_port_bindings(self.redis_port, 6379)
        container_config = dict(name='idmtools_redis', hostname='redis', image=self.redis_image, ports=port_bindings,
                                volumes=redis_volumes)
        if platform.system() in ["Linux", "Darwin"]:
            container_config['user'] = self.run_as
        container_config.update(self.get_common_config(mem_limit=self.redis_mem_limit,
                                                       mem_reservation=self.redis_mem_reservation))
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Redis Config: {container_config}")
        return container_config

    def get_postgres(self, create=True) -> Container:
        """
        Gets the postgres container

        Args:
            create: When set to true, container is created if it is not found

        Returns:
            (Optional[Container]): A Container object is always returned When used with *create=True*. It is possible
            that *None* is returned when *create=False*
        """
        logger.debug('Checking postgres is running')
        postgres_container = self.client.containers.list(filters=dict(name='idmtools_postgres'), all=True)
        if not postgres_container and create:
            container_config = self.create_postgres_config()
            logger.debug(f'Postgres Container Config {str(container_config)}')
            # Create our data volume
            self.create_postgres_volume()
            # Create our container
            postgres_container = self.client.containers.run(**container_config)
        elif type(postgres_container) is list and len(postgres_container):
            postgres_container = postgres_container[0]
            if create:
                postgres_container = self.ensure_container_running(postgres_container)
        return postgres_container

    def create_postgres_config(self):
        """
        Returns the docker config for the postgres container

        Returns:
            (dict) Dictionary representing the docker config for the postgres container
        """

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
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Postgres Config: {container_config}")
        return container_config

    def create_postgres_volume(self) -> NoReturn:
        """
        Creates our postgres volume
        Returns:

        """
        postgres_volume = self.client.volumes.list(filters=dict(name='idmtools_local_postgres'))
        if not postgres_volume:
            self.client.volumes.create(name='idmtools_local_postgres')

    @staticmethod
    def _get_optional_port_bindings(src_port: Optional[Union[str, int]], dest_port: Optional[Union[str, int]]) -> \
            Optional[dict]:
        """
        Used to generate port bindings configurations if the inputs are not set to none

        Args:
            src_port: Host Port
            dest_port:  Container Port

        Returns:
            (Optional[dict]) Dictionary representing the docker port bindings configuration for port if all inputs have
            values
        """
        return {dest_port: src_port} if src_port is not None and dest_port is not None else None

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
