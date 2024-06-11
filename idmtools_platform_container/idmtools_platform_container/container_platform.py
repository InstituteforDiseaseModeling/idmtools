"""
Here we implement the ContainerPlatform object.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import os
import docker
import platform
import subprocess
from uuid import uuid4
from typing import Union, Any
from dataclasses import dataclass, field
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools_platform_container.container_operations.docker_operations import ensure_docker_daemon_running
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

    def submit_job(self, item: Union[Experiment, Simulation], dry_run: bool = False, **kwargs) -> Any:
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
                logger.debug("Build Suite/Experiment/Simulation files!")
            container_id = self.check_container(**kwargs)
            if logger.isEnabledFor(DEBUG):
                logger.debug(f"Container started successfully: {container_id}")

            if platform.system() in ["Windows"]:
                if logger.isEnabledFor(DEBUG):
                    logger.debug("Build Suite/Experiment/Simulation files on Windows!")
                self.convert_scripts_to_linux(container_id, item, **kwargs)

            # submit the experiment/simulations
            if logger.isEnabledFor(DEBUG):
                logger.debug(f"Submit experiment/simulations to container: {container_id}!")
            result = self.submit_experiment(container_id, item, **kwargs)
            return result

        elif isinstance(item, Simulation):
            raise NotImplementedError("submit_job directly for simulation is not implemented on ContainerPlatform.")
        else:
            raise NotImplementedError(
                f"Submit job is not implemented for {item.__class__.__name__} on ContainerPlatform.")

    def check_container(self, **kwargs) -> Any:
        """
        Check the container status.
        Args:
            kwargs: keyword arguments used to expand functionality
        Returns:
            Any
        """
        container_id = ensure_docker_daemon_running(self, **kwargs)
        return container_id

    def start_container(self, **kwargs) -> Any:
        """
        Execute a command in a container.
        Args:
            kwargs: keyword arguments used to expand functionality
        Returns:
            Any
        """
        # Create a Docker client
        client = docker.from_env()

        # Define the source and destination directories for the volume mapping
        data_source_dir = os.path.abspath(self.job_directory)
        data_destination_dir = self.data_mount

        # Define the default volume mapping
        volumes = {
            data_source_dir: {"bind": data_destination_dir, "mode": "rw"}
        }

        # Add user-defined volume mappings
        if self.user_mounts is not None:
            for key, value in self.user_mounts.items():
                volumes[key] = {"bind": value, "mode": "rw"}

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

        # Output the container ID
        if logger.isEnabledFor(DEBUG):
            logger.debug(f"Container ID: {container.id}")

        return container.id

    def convert_scripts_to_linux(self, container_id: str, experiment: Experiment, **kwargs) -> Any:
        """
        Convert the scripts to Linux format.
        Args:
            container_id: container ID
            experiment: idmtools Experiment
            kwargs: keyword arguments used to expand functionality
        Returns:
            Any
        """
        directory = os.path.join(self.data_mount, experiment.parent_id, experiment.id)
        directory = directory.replace("\\", '/')

        try:
            commands = [
                f"cd {directory}",
                r"sed -i 's/\r//g' batch.sh;sed -i 's/\r//g' run_simulation.sh"
            ]

            # Constructing the overall command
            full_command = ["docker", "exec", container_id, "bash", "-c", ";".join(commands)]
            # Execute the command
            result = subprocess.run(full_command, stdout=subprocess.PIPE)

        except subprocess.CalledProcessError as e:
            print("Error executing command:", e)
        except Exception as ex:
            print("Error:", ex)

    def submit_experiment(self, container_id, experiment: Experiment, **kwargs) -> Any:
        directory = os.path.join(self.data_mount, experiment.parent_id, experiment.id)
        directory = str(directory).replace("\\", '/')
        if logger.isEnabledFor(DEBUG):
            logger.debug(f"Directory: {directory}")
            logger.debug(f"container_id: {container_id}")

        try:
            # Commands to change directory and run the script
            commands = [
                f"cd {directory}",
                "bash batch.sh &"
            ]

            # Constructing the overall command
            full_command = ["docker", "exec", container_id, "bash", "-c", ";".join(commands)]

            # Execute the command
            result = subprocess.run(full_command, stdout=subprocess.PIPE)
            if logger.isEnabledFor(DEBUG):
                logger.debug(f"Result from submit: {result}")

        except subprocess.CalledProcessError as e:
            print("Error executing command:", e)
        except Exception as ex:
            print("Error:", ex)
