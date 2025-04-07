"""
Here we implement the ContainerPlatform object.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import os
import docker
import platform
import subprocess
from uuid import uuid4
from docker.models.containers import Container
from typing import Union, NoReturn, List, Dict
from dataclasses import dataclass, field
from idmtools.core.interfaces.ientity import IEntity
from idmtools.entities import Suite
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools_platform_container.container_operations.docker_operations import validate_container_running, \
    find_container_by_image, compare_mounts, find_running_job, get_container, CONTAINER_STATUS, restart_container, \
    is_docker_installed, is_docker_daemon_running
from idmtools_platform_container.platform_operations.simulation_operations import ContainerPlatformSimulationOperations
from idmtools_platform_container.utils.general import map_container_path
from idmtools_platform_container.utils.job_history import JobHistory
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
    __CONTAINER_IMAGE = "docker-production-public.packages.idmod.org/idmtools/container-rocky-runtime:0.0.4"
    __CONTAINER_MOUNT = "/home/container_data"
    docker_image: str = field(default=None, metadata=dict(help="Docker image to run the container"))
    data_mount: str = field(default=None, metadata=dict(help="Data mount point in the container"))
    user_mounts: dict = field(default=None, metadata=dict(help="User-defined mounts"))
    container_prefix: str = field(default=None, metadata=dict(help="Container name prefix"))
    force_start: bool = field(default=False, metadata=dict(help="Force start a new container"))
    new_container: bool = field(default=False, metadata=dict(help="Start a new container"))
    include_stopped: bool = field(default=False, metadata=dict(help="Include stopped containers"))
    debug: bool = field(default=False, metadata=dict(help="Debug mode"))
    container_id: str = field(default=None, metadata=dict(help="Container Id"))

    def __post_init__(self):
        super().__post_init__()
        self._experiments = ContainerPlatformExperimentOperations(platform=self)
        self._simulations = ContainerPlatformSimulationOperations(platform=self)
        self.job_directory = os.path.abspath(self.job_directory)
        self.run_sequence = False
        if self.docker_image is None:
            self.docker_image = self.__CONTAINER_IMAGE
        if self.data_mount is None:
            self.data_mount = self.__CONTAINER_MOUNT

        if self.debug:
            root_logger = getLogger()
            root_logger.setLevel(DEBUG)

        # Check if Docker is installed and running
        if not is_docker_installed():
            user_logger.error("Docker is not installed.")
            exit(-1)
        if not is_docker_daemon_running():
            user_logger.error("Docker daemon is not running.")
            exit(-1)

    def validate_container(self, container_id: str) -> str:
        """
        Validate the container.
        Args:
            container_id: container id
        Returns:
            Container short id
        """
        # Check if the container exists
        container = get_container(container_id)
        if not container:
            user_logger.warning(f"Container {container_id} is not found.")
            exit(-1)

        # Check if the container is in the right status
        if container.status not in CONTAINER_STATUS:
            user_logger.warning(
                f"Container {container_id} is in {container.status} status, but we only support status: {CONTAINER_STATUS}.")
            exit(-1)

        # Check if the container is running if we do not include stopped containers
        if not self.include_stopped and container.status != 'running':
            user_logger.warning(f"Container {container_id} is not running.")
            exit(-1)

        # Check if the container matches the platform mounts
        if not self.validate_mount(container):
            user_logger.warning(f"Container {container_id} does not match the platform mounts.")
            exit(-1)

        # Restart the container if it is not running
        if container.status != 'running':
            restart_container(container)

        return container.short_id

    def run_items(self, items: Union[IEntity, List[IEntity]], **kwargs):
        """
        Run items on the platform.
        Args:
            items: Runnable items
            kwargs: additional arguments
        Returns:
            None
        """
        if self.container_id is not None:
            self.container_id = self.validate_container(self.container_id)
        super().run_items(items, **kwargs)

    def submit_job(self, item: Union[Experiment, Simulation], dry_run: bool = False, **kwargs) -> NoReturn:
        """
        Submit a Process job in a docker container.
        Args:
            item: Experiment or Simulation
            dry_run: True/False
            kwargs: keyword arguments used to expand functionality
        Returns:
            Any
        """
        if dry_run:
            user_logger.info(f'\nDry run: {dry_run}')
            return

        if isinstance(item, Experiment):
            if logger.isEnabledFor(DEBUG):
                logger.debug("Run experiment on container!")

            # Check if the experiment is already running
            his_job = JobHistory.get_job(item.id)
            if his_job:
                job = find_running_job(item.id, his_job['CONTAINER'])
                if job:
                    user_logger.warning(f"Experiment {item.id} is already running on Container {job.container_id}.")
                    exit(-1)

            # Start the container
            if self.container_id is None:
                if logger.isEnabledFor(DEBUG):
                    logger.debug("Check provided container!")
                self.container_id = self.check_container(**kwargs)

            # If the platform is Windows, convert the scripts to Linux format
            if platform.system() in ["Windows"]:
                if logger.isEnabledFor(DEBUG):
                    logger.debug("Script runs on Windows!")
                self.convert_scripts_to_linux(item, **kwargs)

            # Submit the experiment/simulations
            if logger.isEnabledFor(DEBUG):
                logger.debug(f"Submit experiment/simulations to container: {self.container_id}")
            self.submit_experiment(item, **kwargs)

            # Save the job to history
            JobHistory.save_job(self.job_directory, self.container_id, item, self)
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
        container_id = validate_container_running(self, **kwargs)
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
            user_logger.warning(f"Failed to convert script: {e}")
        except Exception as ex:
            user_logger.warning(f"Failed to convert script to Linux: {ex}")

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
            command = f'exec -a "EXPERIMENT:{experiment.id}" bash batch.sh &'
            # Constructing the overall command
            full_command = ["docker", "exec", "--workdir", directory, self.container_id, "bash", "-c", command]

            # Execute the command using Popen for handling background processes
            subprocess.Popen(full_command)

            # Optionally, you can wait for a short period to ensure the command starts
            # process = subprocess.Popen(full_command)
            # process.wait(timeout=5)

            logger.debug(f"Submit experiment {experiment.id} successfully")
        except subprocess.TimeoutExpired:
            user_logger.error(f"Submit experiment {experiment.id} timed out")
            exit(-1)
        except Exception as ex:
            user_logger.error(f"Submit experiment {experiment.id} encounter Error: {ex}")
            exit(-1)

    def build_binding_volumes(self) -> Dict:
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

    def validate_mount(self, container: Union[str, Container]) -> bool:
        """
        Compare the mounts of the container with the platform.
        Args:
            container: a container object or id.
        Returns:
            True/False
        """
        if isinstance(container, str):
            ct = get_container(container)
        else:
            ct = container

        if ct is None:
            logger.warning(f"Container {container} is not found.")
            return False
        mounts1 = self.get_mounts()
        mounts2 = ct.attrs['Mounts']
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

    def retrieve_match_containers(self, image: str = None) -> List:
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
