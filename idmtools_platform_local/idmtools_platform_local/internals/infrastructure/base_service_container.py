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


@dataclass
class BaseServiceContainer(ABC):
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

    def get(self) -> Union[Container, None]:
        container = self.client.containers.list(filters=dict(name=self.container_name), all=True)
        container = [x for x in container if x.name == self.container_name]
        if container:
            if logger.isEnabledFor(DEBUG):
                logger.debug(f"Found {container[0].name}")
            return container[0]
        return None

    def get_or_create(self, spinner=None) -> Container:
        container = self.get()
        if container is None:
            if logger.isEnabledFor(DEBUG):
                logger.debug(f"Creating {self.__class__.__name__}")
            container = self.create(spinner)
        else:
            self.ensure_container_is_running(container)
        return container

    @staticmethod
    def ensure_container_is_running(container) -> Container:
        if container.status in ['exited', 'created']:
            logger.debug(f"Restarting container: {container.name}")
            container.start()
            container.reload()
        return container

    def create(self, spinner=None) -> Container:
        retries = 0
        while retries < 3:
            try:
                container_config = self.get_configuration()
                if logger.isEnabledFor(DEBUG):
                    logger.debug(f'Container Config {str(container_config)}')
                container = self.client.containers.run(**container_config)
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

    def stop(self, remove=False):
        container = self.get()
        if container:
            container.stop()
            if remove:
                container.remove()

    def restart(self):
        container = self.get()
        if container:
            container.restart()

    @abstractmethod
    def get_configuration(self) -> Dict:
        pass
