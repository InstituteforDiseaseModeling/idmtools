"""
Here we implement the ContainerPlatform docker operations.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import docker
import subprocess
from typing import List, Dict, NoReturn, Any
from logging import getLogger, DEBUG
from idmtools_platform_container.utils import normalize_path
from docker.errors import NotFound as ErrorNotFound
from docker.errors import APIError as DockerAPIError

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
        exit(-1)

    if not is_docker_daemon_running():
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
    container_match = platform.retrieve_match_containers(**kwargs)
    container_running = [container for status, container in container_match if status == 'running']
    container_stopped = [container for status, container in container_match if status != 'running']

    if logger.isEnabledFor(DEBUG):
        logger.debug(f"Found running matched containers: {container_running}")
        if platform.include_stopped:
            logger.debug(f"Found stopped matched containers: {container_stopped}")

    if platform.force_start:
        if logger.isEnabledFor(DEBUG) and len(container_running) > 0:
            logger.debug(f"Stop all running containers {container_running}")
        stop_all_containers(container_running)
        container_running = []

        if logger.isEnabledFor(DEBUG) and len(container_stopped) > 0 and platform.include_stopped:
            logger.debug(f"Stop all stopped containers {container_stopped}")
        stop_all_containers(container_stopped)
        container_stopped = []

    if not platform.new_container:
        if len(container_running) > 0:
            # Pick up the first running container
            container_id = container_running[0].short_id
            if logger.isEnabledFor(DEBUG):
                logger.debug(f"Pick running container {container_id}.")
        elif len(container_stopped) > 0:
            # Pick up the first stopped container and then restart it
            container = container_stopped[0]
            container.restart()
            container_id = container.short_id
            if logger.isEnabledFor(DEBUG):
                logger.debug(f"Pick and restart the stopped container {container_stopped[0].short_id}.")

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


def stop_container(container) -> NoReturn:
    """
    Stop a container.
    Args:
        container: a container object to be stopped
    Returns:
        No return
    """
    try:
        # Stop the container
        container.stop()
        container.remove()
        if logger.isEnabledFor(DEBUG):
            logger.debug(f"Container with ID {container.short_id} has been stopped.")
    except ErrorNotFound:
        logger.debug(f"Container with ID {container.short_id} not found.")
    except DockerAPIError as e:
        logger.debug(f"Error stopping container with ID {container.short_id}: {str(e)}")


def stop_all_containers(containers: List) -> NoReturn:
    """
    Stop all containers.
    Args:
        containers: list of containers to be stopped
    Returns:
        No return
    """
    for container in containers:
        stop_container(container)


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
            logger.debug("Docker daemon is not running:", e)
        return False
    except Exception as ex:
        if logger.isEnabledFor(DEBUG):
            logger.debug("Error checking Docker daemon:", ex)
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
def compare_mounts(mounts1: List[Dict], mounts2:List[Dict]) -> bool:
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
