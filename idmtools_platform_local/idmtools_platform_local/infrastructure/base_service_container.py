"""idmtools base service container.

This defined the base docker container. We use this amongst each service to build our containers as needed.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import difflib
import io
import json
import tarfile
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from getpass import getpass
from logging import getLogger, DEBUG
from typing import Optional, Union, Dict, List
from docker.errors import APIError
from idmtools_platform_local import __version__
from docker import DockerClient
from docker.models.containers import Container

logger = getLogger(__name__)
user_logger = getLogger('user')


@dataclass
class BaseServiceContainer(ABC):
    """Providers base abstract class for local platform container objects/managers."""
    container_name: str = None
    image: str = None
    client: DockerClient = None
    config_prefix: str = None
    network: str = None

    @staticmethod
    def get_common_config(container_name: str, image: str, network: str, port_bindings: Optional[Dict] = None,
                          volumes: Optional[Dict] = None,
                          mem_limit: Optional[str] = None, mem_reservation: Optional[str] = None,
                          environment: Optional[List[str]] = None,
                          extra_labels: Optional[Dict] = None, **extras) -> dict:
        """
        Returns portions of docker container configs that are common between all the different containers used within our platform.

        Args:
            container_name: Container name
            image: Image to use
            network: Network to use
            port_bindings: Port binding
            volumes: Volume definitions
            mem_limit: Memory limit
            mem_reservation: Memory reservation
            environment: Environment vars
            extra_labels: Extra labels to use
            **extras:

        Returns:
            Common configuration object to use when creating a container.

        Notes:
            Memory strings should match those used by docker. See --memory details at
            https://docs.docker.com/engine/reference/run/#runtime-constraints-on-resources
        """
        config = dict(
            name=container_name, image=image, hostname=container_name, network=network,
            restart_policy=dict(MaximumRetryCount=15, name='on-failure'),
            detach=True,
            labels=dict(idmtools_version=__version__)
        )
        if port_bindings:
            config['ports'] = port_bindings
        if volumes:
            config['volumes'] = volumes
        if environment:
            config['environment'] = environment
        if extra_labels:
            config['labels'].update(extra_labels)
        if mem_limit:
            config['mem_limit'] = mem_limit
        if mem_reservation:
            config['mem_reservation'] = mem_reservation
        if extras:
            config.update(extras)
        return config

    @staticmethod
    def _get_optional_port_bindings(src_port: Optional[Union[str, int]], dest_port: Optional[Union[str, int]]) -> Optional[dict]:
        """
        Used to generate port bindings configurations if the inputs are not set to none.

        Args:
            src_port: Host Port
            dest_port:  Container Port

        Returns:
            (Optional[dict]) Dictionary representing the docker port bindings configuration for port if all inputs have
            values
        """
        return {dest_port: src_port} if src_port is not None and dest_port is not None else None

    def get(self) -> Union[Container, None]:
        """
        Get the container.

        Returns:
            Container if it is running.
        """
        container = self.client.containers.list(filters=dict(name=self.container_name), all=True)
        container = [x for x in container if x.name == self.container_name]
        if container:
            container = container[0]
            if logger.isEnabledFor(DEBUG):
                logger.debug(f"Found {container.name}")
            return container
        return None

    def get_or_create(self, spinner=None) -> Container:
        """
        Get or Create a container.

        Args:
            spinner: Optional spinner to display

        Returns:
            Docker container object representing service container
        """
        container = self.get()
        if container is None:
            if logger.isEnabledFor(DEBUG):
                logger.debug(f"Creating {self.__class__.__name__}")
            container = self.create(spinner)
        else:
            self.ensure_container_is_running(container, spinner)
        return container

    def ensure_container_is_running(self, container: Container, spinner=None) -> Container:
        """
        Ensures is running.

        Args:
            container:container to check if it is running
            spinner: Optional spinner to show we are busy while checking.

        Returns:
            Container
        """
        if container.status in ['exited', 'created']:
            logger.debug(f"Restarting container: {container.name}")
            container.start()
            container.reload()
        else:
            # validate config matched what we expect
            if self.has_different_config(container):
                self.stop(remove=True, container=container)
                container = self.create(spinner)
        return container

    def has_different_config(self, container, show_diff: bool = True):
        """
        Detect if the config is difference that running container.

        Args:
            container: Container
            show_diff: Should we display diff

        Returns:
            True if there is differing configuration
        """
        running_config = self.get_running_config(container)
        current_config = json.dumps(self.get_configuration(), indent=4, sort_keys=True)
        if current_config != running_config:
            if show_diff:
                lines = difflib.unified_diff(running_config.split("\n"), current_config.split("\n"))
                user_logger.info(f"Configuration changed for {self.container_name}\n")
                user_logger.info("\n".join(lines))
            return True
        return False

    def get_running_config(self, container):
        """
        Fetches the config used to start a container.

        Args:
            container:Container to use

        Returns:
            The config from the running container.
        """
        stream, stat = container.get_archive("/local_config.json")
        file_obj = io.BytesIO()
        for i in stream:
            file_obj.write(i)
        file_obj.seek(0)
        tar = tarfile.open(mode='r', fileobj=file_obj)
        running_config = tar.extractfile('local_config.json').read().decode("utf-8")
        if logger.isEnabledFor(DEBUG):
            logger.debug(f"Running Config for {self.container_name}.\n{running_config}")
        return running_config

    @staticmethod
    def copy_config_to_container(container: Container, config: dict):
        """
        Copy the configuration used to create container to a container for future reference.

        Args:
            container: Target container
            config: Config to copy

        Returns:
            None
        """
        if logger.isEnabledFor(DEBUG):
            logger.debug("Copying config used to create container to container")
        file_like_object = io.BytesIO(initial_bytes=json.dumps(config, indent=4, sort_keys=True).encode('utf-8'))
        tar_memory = io.BytesIO()
        tar = tarfile.open(fileobj=tar_memory, mode='w')
        try:
            ti = tarfile.TarInfo('local_config.json')
            ti.size = len(file_like_object.getvalue())
            tar.addfile(ti, file_like_object)
        finally:
            tar.close()
        tar_memory.seek(0)
        container.put_archive("/", tar_memory.read())

    def create(self, spinner=None) -> Container:
        """
        Create our container.

        Args:
            spinner: Optional spinner. When provided, we will use it to indicate we are busy during long-running tasks.

        Returns:
            Created Container.

        Raises:
            EnvironmentError - If a container tries to start with a port in use
            ValueError - Unkown cause
        Notes:
            - TODO - Add Exception for environment error with doc_link
        """
        retries = 0
        while retries < 3:
            try:
                container_config = self.get_configuration()
                if logger.isEnabledFor(DEBUG):
                    logger.debug(f'Container Config {str(container_config)}')
                container = self.client.containers.run(**container_config)
                # give some start time to containers
                time.sleep(0.25)
                # check status of container until it is no longer starting/created
                self.wait_on_status(container)
                logger.debug(f'{self.container_name}: {container.status}: {container.id}')
                if container.status in ['failed']:
                    raise EnvironmentError(f"Could not start {self.__class__.__name__}")
                self.copy_config_to_container(container, container_config)
                return container
            except APIError as e:
                retries += 1
                if logger.isEnabledFor(DEBUG):
                    logger.exception(e)

                if e.status_code == 409:
                    self.stop(True)
                elif e.status_code in [500]:
                    content = e.response.json()
                    if 'message' in content and 'unauthorized' in content['message']:
                        if spinner:
                            spinner.hide()
                        registry = self.image.split("/")[0]
                        print(f"\nAuthentication needed for {registry}.\nIt is best to login manually outside of "
                              f"idmtools using\n docker login {registry}\nas this will save your password\n"
                              f"Prompting for credentials for one time user:\n")
                        username = input(f'{registry} Username:')
                        password = getpass('Password:')
                        self.client.login(username, password, registry=registry)
                        if spinner:
                            spinner.show()
                    elif 'message' in content and 'address already in use' in content['message']:
                        raise EnvironmentError(f"Could not start docker service {self.container_name} due to a port"
                                               f" being already in use. See Full error: {content['message']}")
                elif e.status_code == 404:
                    print(f'\n\nCould not locate a docker image with the tag: {self.image}\n'
                          f'Please check the name of the image or ensure you have built that image locally.'
                          f'You can test a manual pull using \n'
                          f'docker pull {self.image}')
                    raise e
                else:
                    raise e

        if retries > 2:
            raise ValueError("Could not run workers image. Likely causes are:\n\t- A used port"
                             "\n\t-A service being down such as redis or postgres"
                             "\n\t-Authentication issues with the docker registry")

    @staticmethod
    def wait_on_status(container, sleep_interval: float = 0.2, max_time: float = 2, statutes_to_wait_for: List[str] = None):
        """
        Wait on a container to achieve a specific status.

        Args:
            container: Target container
            sleep_interval: How long to wait between checks
            max_time: Max time to wait(default to 2 seconds)
            statutes_to_wait_for: List of statuss to wait for. When not set, we use starting and created.

        Returns:
            None
        """
        if statutes_to_wait_for is None:
            statutes_to_wait_for = ['starting', 'created']
        start = time.time()
        if logger.isEnabledFor(DEBUG):
            logger.debug(f'Waiting on {container.name} to become in {statutes_to_wait_for}')
        while container.status in statutes_to_wait_for and (time.time() - start) < max_time:
            time.sleep(sleep_interval)
            container.reload()

    def stop(self, remove=False, container: Container = None):
        """
        Stop a container.

        Args:
            remove: When true, the container will be removed after being stopped
            container: Container to stop

        Returns:
            None
        """
        if container is None:
            container = self.get()
        if container:
            if logger.isEnabledFor(DEBUG):
                logger.debug(f'Stopping container: {container.name}')
            container.stop()
            if remove:
                if logger.isEnabledFor(DEBUG):
                    logger.debug(f'Removing container: {container.name}')
                container.remove()

    def restart(self, container: Container = None):
        """
        Restart a container.

        Args:
            container: Container to restart.

        Returns:
            None
        """
        if container is None:
            container = self.get()
        if container:
            if logger.isEnabledFor(DEBUG):
                logger.debug(f'Restarting container: {container.name}')
            container.restart()
            if logger.isEnabledFor(DEBUG):
                logger.debug(f'Container restarted: {container.name}')

    def get_logs(self):
        """
        Get logs from container.

        Returns:
            Container logs as a string.
        """
        container = self.get()
        if container:
            if logger.isEnabledFor(DEBUG):
                logger.debug(f'Get container logs: {container.name}')
            logs = container.logs()
            if logs:
                logs = logs.decode('utf-8')
            return logs
        return ''

    @abstractmethod
    def get_configuration(self) -> Dict:
        """
        Get configuration.

        Each sub-class should define this to provide their own specific configuration.

        Returns:
            Configuration dict
        """
        pass
