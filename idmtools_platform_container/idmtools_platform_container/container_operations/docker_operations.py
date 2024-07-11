"""
Here we implement the ContainerPlatform docker operations.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import docker
import subprocess
from dataclasses import dataclass
from typing import List, Dict, NoReturn, Any, Union
from idmtools.core import ItemType
from idmtools_platform_container.utils.general import normalize_path, parse_iso8601
from docker.models.containers import Container
from docker.errors import NotFound as ErrorNotFound
from docker.errors import APIError as DockerAPIError
from logging import getLogger, DEBUG

logger = getLogger(__name__)
user_logger = getLogger('user')

# Only consider the containers that can be restarted
CONTAINER_STATUS = ['exited', 'running', 'paused']


def validate_container_running(platform, **kwargs) -> str:
    """
    Check if the docker daemon is running, find existing container or start a new container.
    Args:
        platform: Platform
        kwargs: keyword arguments used to expand functionality
    Returns:
        container id
    """
    if not is_docker_installed():
        user_logger.error("Docker is not installed.")
        exit(-1)

    if not is_docker_daemon_running():
        user_logger.error("Docker daemon is not running.")
        exit(-1)

    # Check image exists
    if not check_local_image(platform.docker_image):
        user_logger.info(f"Image {platform.docker_image} does not exist, pull the image first.")
        succeeded = pull_docker_image(platform.docker_image)
        if not succeeded:
            user_logger.error(f"/!\\ ERROR: Failed to pull image {platform.docker_image}.")
            exit(-1)

    # User configuration
    if logger.isEnabledFor(DEBUG):
        logger.debug(f"User config: force_start={platform.force_start}")
        logger.debug(f"User config: new_container={platform.new_container}")
        logger.debug(f"User config: include_stopped={platform.include_stopped}")

    # Check containers
    container_id = None
    container_match = platform.retrieve_match_containers()
    container_running = [container for status, container in container_match if status == 'running']
    container_stopped = [container for status, container in container_match if status != 'running']

    if logger.isEnabledFor(DEBUG):
        logger.debug(f"Found running matched containers: {container_running}")
        if platform.include_stopped:
            logger.debug(f"Found stopped matched containers: {container_stopped}")

    if platform.force_start:
        if logger.isEnabledFor(DEBUG) and len(container_running) > 0:
            logger.debug(f"Stop all running containers {container_running}")
        stop_all_containers(container_running, keep_running=False)
        container_running = []

        if logger.isEnabledFor(DEBUG) and len(container_stopped) > 0 and platform.include_stopped:
            logger.debug(f"Stop all stopped containers {container_stopped}")
        stop_all_containers(container_stopped, keep_running=False)
        container_stopped = []

    if not platform.new_container and platform.container_prefix is None:
        if len(container_running) > 0:
            # Pick up the first running container
            container_running = sort_containers_by_start(container_running)
            container_id = container_running[0].short_id
            if logger.isEnabledFor(DEBUG):
                logger.debug(f"Pick running container {container_id}.")
        elif len(container_stopped) > 0:
            # Pick up the first stopped container and then restart it
            container_stopped = sort_containers_by_start(container_stopped)
            container = container_stopped[0]
            container.restart()
            container_id = container.short_id
            if logger.isEnabledFor(DEBUG):
                logger.debug(f"Pick and restart the stopped container {container.short_id}.")

    # Start the container
    if container_id is None:
        container_id = platform.start_container(**kwargs)
        if logger.isEnabledFor(DEBUG):
            logger.debug(f"Start container: {platform.docker_image}")
            logger.debug(f"New container ID: {container_id}")

    return container_id


#############################
# Check containers
#############################

def get_container(container_id) -> Any:
    """
    Get the container object by container ID.
    Args:
        container_id: container id
    Returns:
        container object
    """
    client = docker.from_env()

    try:
        # Retrieve the container
        container = client.containers.get(container_id)
        return container
    except ErrorNotFound:
        user_logger.debug(f"Container with ID {container_id} not found.")
        return None
    except DockerAPIError as e:
        user_logger.debug(f"Error retrieving container with ID {container_id}: {str(e)}")
        return None


def find_container_by_image(image: str, include_stopped: bool = False) -> Dict:
    """
    Find the containers that match the image.
    Args:
        image: docker image
        include_stopped: bool, if consider the stopped containers or not
    Returns:
        dict of containers
    """
    client = docker.from_env()
    container_found = {}
    for container in client.containers.list(all=include_stopped):
        if container.status not in CONTAINER_STATUS:
            continue
        if image in container.image.tags:
            if logger.isEnabledFor(DEBUG):
                logger.debug(f"Image {image} found in container ({container.status}): {container.short_id}")
            if container_found.get(container.status, None) is None:
                container_found[container.status] = []
            container_found[container.status].append(container)

    return container_found


def stop_container(container: Union[str, Container], remove: bool = True) -> NoReturn:
    """
    Stop a container.
    Args:
        container: container id  or container object to be stopped
        remove: bool, if remove the container or not
    Returns:
        No return
    """
    try:
        if isinstance(container, str):
            container = get_container(container)
        elif not isinstance(container, Container):
            raise TypeError("Invalid container object.")

        # Stop the container
        if container.status == 'running':
            container.stop()
            if logger.isEnabledFor(DEBUG):
                logger.debug(f"Container {str(container)} has been stopped.")

        if remove:
            container.remove()
            if logger.isEnabledFor(DEBUG):
                logger.debug(f"Container {str(container)} has been removed.")
    except ErrorNotFound:
        if isinstance(container, str):
            logger.debug(f"Container with ID {container} not found.")
        else:
            logger.debug(f"Container {container.short_id} not found.")
    except DockerAPIError as e:
        logger.debug(f"Error stopping container {str(container)}: {str(e)}")


def stop_all_containers(containers: List[Union[str, Container]], keep_running: bool = True,
                        remove: bool = True) -> NoReturn:
    """
    Stop all containers.
    Args:
        containers: list of container id or containers to be stopped
        keep_running: bool, if keep the running containers or not
        remove: bool, if remove the container or not
    Returns:
        No return
    """
    for container in containers:
        if container.status == 'running' and keep_running:
            jobs = list_running_jobs(container.short_id)
            if jobs:
                continue
        stop_container(container, remove=remove)


def sort_containers_by_start(containers: List[Container], reverse: bool = True) -> List[Container]:
    """
    Sort the containers by the start time.
    Args:
        containers: list of containers
        reverse: bool, if sort in reverse order
    Returns:
        sorted list of containers
    """
    # Sort containers by 'StartedAt' in descending order
    sorted_container_list = sorted(
        containers,
        key=lambda container: parse_iso8601(container.attrs['State']['StartedAt']),
        reverse=reverse
    )

    return sorted_container_list


def list_running_containers() -> List[Container]:
    """
    List all running containers.
    Returns:
        list of running containers
    """
    client = docker.from_env()
    return client.containers.list()


def list_containers(include_stopped: bool = False) -> Dict:
    """
    Find the containers that match the image.
    Args:
        include_stopped: bool, if consider the stopped containers or not
    Returns:
        dict of containers
    """
    client = docker.from_env()
    container_found = {}
    for container in client.containers.list(all=include_stopped):
        if container.status not in CONTAINER_STATUS:
            continue
        if container_found.get(container.status, None) is None:
            container_found[container.status] = []
        container_found[container.status].append(container)

    return container_found


#############################
# Check docker
#############################

def is_docker_installed() -> bool:
    """
    Check if Docker is installed.
    Returns:
        True/False
    """
    try:
        # Run the 'docker --version' command
        result = subprocess.run(['docker', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # Check the return code to see if it executed successfully
        if result.returncode == 0:
            if logger.isEnabledFor(DEBUG):
                logger.debug(f"Docker is installed: {result.stdout.strip()}")
            return True
        else:
            if logger.isEnabledFor(DEBUG):
                logger.debug(f"Docker is not installed. Error: {result.stderr.strip()}")
            return False
    except FileNotFoundError:
        # If the docker executable is not found, it means Docker is not installed
        if logger.isEnabledFor(DEBUG):
            logger.debug("Docker is not installed or not found in PATH.")
        return False


def is_docker_daemon_running() -> bool:
    """
    Check if the Docker daemon is running.
    Returns:
        True/False
    """
    try:
        client = docker.from_env()
        client.ping()
        if logger.isEnabledFor(DEBUG):
            logger.debug("Docker daemon is running.")
        return True
    except DockerAPIError as e:
        if logger.isEnabledFor(DEBUG):
            logger.debug(f"Docker daemon is not running: {e}")
        return False
    except Exception as ex:
        if logger.isEnabledFor(DEBUG):
            logger.debug(f"Error checking Docker daemon: {ex}")
        return False


#############################
# Check images
#############################

def check_local_image(image_name: str) -> bool:
    """
    Check if the image exists locally.
    Args:
        image_name: image name
    Returns:
        True/False
    """
    client = docker.from_env()
    for image in client.images.list():
        if image_name in image.tags:
            return True
    return False


def pull_docker_image(image_name, tag='latest') -> bool:
    """
    Pull a docker image from IDM artifactory.
    Args:
        image_name: image name
        tag: image tag
    Returns:
        True/False
    """
    if ':' in image_name:
        full_image_name = image_name
    else:
        full_image_name = f'{image_name}:{tag}'

    user_logger.info(f'Pulling image {full_image_name} ...')
    try:
        client = docker.from_env()
        client.images.pull(f'{full_image_name}')
        if logger.isEnabledFor(DEBUG):
            logger.debug(f'Successfully pulled {full_image_name}')
        return True
    except DockerAPIError as e:
        if logger.isEnabledFor(DEBUG):
            logger.debug(f'Error pulling {full_image_name}: {e}')
        return False


#############################
# Check binding/mounting
#############################
def compare_mounts(mounts1: List[Dict], mounts2: List[Dict]) -> bool:
    """
    Compare two sets of mount configurations.
    Args:
        mounts1: container mounting configurations
        mounts2: container mounting configurations
    Returns:
        True/False
    """
    # Convert mount configurations to a set of tuples for easy comparison
    mounts_set1 = set(
        (mount['Type'], mount['Mode'], normalize_path(mount['Source']), normalize_path(mount['Destination'])) for
        mount in mounts1
    )
    mounts_set2 = set(
        (mount['Type'], mount['Mode'], normalize_path(mount['Source']), normalize_path(mount['Destination'])) for
        mount in mounts2
    )

    return mounts_set1 == mounts_set2


def compare_container_mount(container_id1: str, container_id2: str) -> bool:
    """
    Compare the mount configurations of two containers.
    Args:
        container_id1: container id
        container_id2: container id
    Returns:
        True/False
    """
    container1 = get_container(container_id1)
    container2 = get_container(container_id2)

    mounts1 = container1.attrs['Mounts']
    mounts2 = container2.attrs['Mounts']

    return compare_mounts(mounts1, mounts2)


#############################
# Check jobs
#############################

PS_QUERY = 'ps xao pid,ppid,pgid,cmd | head -n 1 && ps xao pid,ppid,pgid,cmd | grep -e EXPERIMENT -e SIMULATION | grep -v grep'


@dataclass(repr=False)
class Job:
    """Running Job."""
    item_id: str = None
    item_type: ItemType = None
    job_id: int = None
    group_pid: int = None
    container_id: str = None
    created: str = None

    def __init__(self, container_id: str, process_line: str):
        """
        Initialize Job.
        Args:
            container_id: Container ID
            process_line: Pricess Input Line
        """
        process = process_line.split()
        parts = process[3].split(':')
        self.item_id = parts[1]
        self.group_pid = int(process[2])
        self.item_type = ItemType.EXPERIMENT if parts[0] == 'EXPERIMENT' else ItemType.SIMULATION
        if parts[0] == 'EXPERIMENT':
            self.job_id = int(process[2])
        elif parts[0] == 'SIMULATION':
            self.job_id = int(process[0])
        self.container_id = container_id

    def display(self):
        """Display Job for debugging usage."""
        user_logger.info(f"Item ID: {self.item_id:15}")
        user_logger.info(f"Item Type: {self.item_type:15}")
        user_logger.info(f"Job ID: {self.job_id:15}")
        user_logger.info(f"Group PID: {self.group_pid:15}")
        user_logger.info(f"Container ID: {self.container_id:15}")


def list_running_jobs(container_id: str, limit: int = None) -> List[Job]:
    """
    List all running jobs on the container.
    Args:
        container_id: Container ID
        limit: number of jobs to view
    Returns:
        list of running jobs
    """
    command = f'docker exec {container_id} bash -c "({PS_QUERY})"'
    result = subprocess.run(command, shell=True, check=False, capture_output=True, text=True)

    running_jobs = []
    if result.returncode == 0:
        processes = result.stdout

        for line in processes.splitlines()[1:]:  # Skip the first headerline
            if 'EXPERIMENT' in line or 'SIMULATION' in line:
                job = Job(container_id, line)
                running_jobs.append(job)
    elif result.returncode == 1:
        pass
    else:
        user_logger.error(f"Command failed with return code {result.returncode}")
        user_logger.error(result.stderr)

    if limit:
        running_jobs = running_jobs[:limit]
    return running_jobs[:limit]


def find_running_job(item_id: Union[int, str], container_id: str = None) -> Job:
    """
    Check item running on container.
    Args:
        item_id: Experiment/Simulation ID or Running Job ID
        container_id: Container ID
    Returns:
        running Job
    """
    if container_id:
        containers = [container_id]
    else:
        containers = [container.short_id for container in list_running_containers()]

    match_jobs = []
    for cid in containers:
        jobs = list_running_jobs(cid)
        if len(jobs) == 0:
            continue

        for job in jobs:
            if job.item_id == item_id or str(job.job_id) == str(item_id):
                match_jobs.append(job)
                break  # One running container can't have multiple matches!

    if len(match_jobs) > 1:
        # item_is must be a Job ID in this case and container_id must be None!
        user_logger.error(
            f"Multiple jobs found for Job ID {item_id}, please provide the Container ID or use Entity ID instead.")
        exit(-1)
    elif len(match_jobs) == 1:
        return match_jobs[0]
    else:
        return None
