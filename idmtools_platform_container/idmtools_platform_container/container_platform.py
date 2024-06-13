"""
Here we implement the ContainerPlatform object.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import os
import docker
import platform
import subprocess
from uuid import uuid4
from typing import Union, NoReturn, List
from dataclasses import dataclass, field
from idmtools.entities import Suite
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools_platform_container.container_operations.docker_operations import ensure_docker_daemon_running, \
    find_container_by_image, compare_mounts
from idmtools_platform_container.utils import map_container_path
from idmtools_platform_file.file_platform import FilePlatform
from idmtools_platform_container.platform_operations.experiment_operations import ContainerPlatformExperimentOperations
from logging import getLogger, DEBUG

logger = getLogger(__name__)
user_logger = getLogger('user')


@dataclass(repr=False)
class ContainerPlatform(FilePlatform):
    """
    Container Platform definition.
    """
    __CONTAINER_IMAGE = "docker-production-public.packages.idmod.org/idmtools/container-test:0.0.3"
    __CONTAINER_MOUNT = "/home/container_data"
    docker_image: str = field(default=None)
    data_mount: str = field(default=None)
    user_mounts: dict = field(default=None)
    container_prefix: str = field(default=None)
    force_start: bool = field(default=False)
    new_container: bool = field(default=False)
    include_stopped: bool = field(default=False)
    debug: bool = field(default=False)
    _container_id: str = field(default=None, init=False)

    def __post_init__(self):
        super().__post_init__()
        self._experiments = ContainerPlatformExperimentOperations(platform=self)
        self.job_directory = os.path.abspath(self.job_directory)
        self.sym_link = False
        self.run_sequence = False
        if self.docker_image is None:
            self.docker_image = self.__CONTAINER_IMAGE
        if self.data_mount is None:
            self.data_mount = self.__CONTAINER_MOUNT

        if self.debug:
            root_logger = getLogger()
            root_logger.setLevel(DEBUG)

    @property
    def container_id(self):  # noqa: F811
        """
        Returns container id.

        Returns:
            container id
        """
        return self._container_id

    @container_id.setter
    def container_id(self, _id):
        """
        Set the container id property.

        Args:
            _id: container id

        Returns:
            None
        """
        self._container_id = _id

    def submit_job(self, item: Union[Experiment, Simulation], dry_run: bool = False, **kwargs) -> NoReturn:
        """
        Submit a Process job in a docker container.
        Args:
            item: idmtools Experiment or Simulation
            dry_run: True/False
            kwargs: keyword arguments used to expand functionality
        Returns:
            Any
        """
        if dry_run:
            user_logger.info(f'Dry run: {item.id}')
            return

        if isinstance(item, Experiment):
            if logger.isEnabledFor(DEBUG):
                logger.debug("Run experiment!")
            self.container_id = self.check_container(**kwargs)

            if platform.system() in ["Windows"]:
                if logger.isEnabledFor(DEBUG):
                    logger.debug("Script runs on Windows!")
                self.convert_scripts_to_linux(item, **kwargs)

            # submit the experiment/simulations
            if logger.isEnabledFor(DEBUG):
                logger.debug(f"Submit experiment/simulations to container: {self.container_id}!")
            self.submit_experiment(item, **kwargs)

        elif isinstance(item, Simulation):
            raise NotImplementedError("submit_job directly for simulation is not implemented on ContainerPlatform.")
        else:
            raise NotImplementedError(
                f"Submit job is not implemented for {item.__class__.__name__} on ContainerPlatform.")

    def check_container(self, **kwargs) -> str:
        """
        Check the container status.
        Args:
            kwargs: keyword arguments used to expand functionality
        Returns:
            container id
        """
        container_id = ensure_docker_daemon_running(self, **kwargs)
        return container_id

    def start_container(self, **kwargs) -> str:
        """
        Execute a command in a container.
        Args:
            kwargs: keyword arguments used to expand functionality
        Returns:
            container id
        """
        # Create a Docker client
        client = docker.from_env()
        volumes = self.build_binding_volumes()

        # Run the container
        container = client.containers.run(
            self.docker_image,
            command="bash",
            volumes=volumes,
            stdin_open=True,
            tty=True,
            detach=True,
            name=f"{self.container_prefix}_{str(uuid4())}" if self.container_prefix else None
        )

        return container.short_id

    def convert_scripts_to_linux(self, experiment: Experiment, **kwargs) -> NoReturn:
        """
        Convert the scripts to Linux format.
        Args:
            experiment: Experiment
            kwargs: keyword arguments used to expand functionality
        Returns:
            No return
        """
        directory = self.get_container_directory(experiment)

        try:
            commands = [
                f"cd {directory}",
                r"sed -i 's/\r//g' batch.sh;sed -i 's/\r//g' run_simulation.sh"
            ]

            # Constructing the overall command
            full_command = ["docker", "exec", self.container_id, "bash", "-c", ";".join(commands)]
            # Execute the command
            subprocess.run(full_command, stdout=subprocess.PIPE)

        except subprocess.CalledProcessError as e:
            print("Error executing command:", e)
        except Exception as ex:
            print("Error:", ex)

    def submit_experiment(self, experiment: Experiment, **kwargs) -> NoReturn:
        """
        Submit an experiment to the container.
        Args:
            experiment: Experiment
            kwargs: keyword arguments used to expand functionality
        Returns:
            No return
        """
        directory = self.get_container_directory(experiment)
        if logger.isEnabledFor(DEBUG):
            logger.debug(f"Directory: {directory}")
            logger.debug(f"container_id: {self.container_id}")

        try:
            # Commands to change directory and run the script
            commands = [
                f"cd {directory}",
                "bash batch.sh &"
            ]

            # Constructing the overall command
            full_command = ["docker", "exec", self.container_id, "bash", "-c", ";".join(commands)]

            # Execute the command
            result = subprocess.run(full_command, stdout=subprocess.PIPE)
            if logger.isEnabledFor(DEBUG):
                logger.debug(f"Result from submit: {result}")

        except subprocess.CalledProcessError as e:
            print("Error executing command:", e)
        except Exception as ex:
            print("Error:", ex)

    def build_binding_volumes(self) -> dict:
        """
        Build the binding volumes for the container.
        Returns:
            bindings in dict format
        """
        volumes = {
            self.job_directory: {"bind": self.data_mount, "mode": "rw"}
        }

        # Add user-defined volume mappings
        if self.user_mounts is not None:
            for key, value in self.user_mounts.items():
                volumes[key] = {"bind": value, "mode": "rw"}

        return volumes

    def get_mounts(self) -> List:
        """
        Build the mounts of the container.
        Returns:
            List of mounts (Dict)
        """
        mounts = []
        mount = {'Type': 'bind',
                 'Source': self.job_directory,
                 'Destination': self.data_mount,
                 'Mode': 'rw'}

        mounts.append(mount)

        # Add user-defined volume mappings
        if self.user_mounts is not None:
            for key, value in self.user_mounts.items():
                mount = {'Type': 'bind',
                         'Source': key,
                         'Destination': value,
                         'Mode': 'rw'}
                mounts.append(mount)

        return mounts

    def validate_mount(self, container) -> bool:
        """
        Compare the mounts of the container with the platform.
        Args:
            container: a container to be compared.
        Returns:
            True/False
        """
        mounts1 = self.get_mounts()
        mounts2 = container.attrs['Mounts']
        return compare_mounts(mounts1, mounts2)

    def get_container_directory(self, item: Union[Suite, Experiment, Simulation]) -> str:
        """
        Get the container corresponding directory of an item.
        Args:
            item: Suite, Experiment or Simulation
        Returns:
            string Path
        """
        item_dir = self.get_directory(item)
        item_container_dir = map_container_path(self.job_directory, self.data_mount, str(item_dir))

        return item_container_dir

    def check_running_container(self, image: str = None) -> List:
        """
        Find the containers that match math the image.
        Args:
            image: docker image
        Returns:
            list of containers
        """
        if image is None:
            image = self.docker_image
        container_found = find_container_by_image(image, self.include_stopped)
        container_match = []
        if len(container_found) > 0:
            for status, containers in container_found.items():
                for container in containers:
                    if self.validate_mount(container):
                        container_match.append((status, container))

            if len(container_match) == 0:
                if logger.isEnabledFor(DEBUG):
                    logger.debug(f"Found container with image {image}, but no one match platform mounts.")
        else:
            if logger.isEnabledFor(DEBUG):
                logger.debug(f"Not found container matching image {image}.")

        return container_match
