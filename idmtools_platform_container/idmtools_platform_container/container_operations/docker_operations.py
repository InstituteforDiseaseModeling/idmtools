import os
import json
import docker
import platform
import subprocess
from typing import Any, List
from logging import getLogger, DEBUG
from idmtools_platform_container.utils import normalize_path

logger = getLogger(__name__)
user_logger = getLogger('user')


def ensure_docker_daemon_running(platform, all: bool = False, **kwargs):
    """
    Check if the docker daemon is running and start it if it is not running.
    Args:
        platform: Platform
        kwargs: additional arguments
    Returns:
        Container ID
    """
    if is_docker_installed():
        if logger.isEnabledFor(DEBUG):
            logger.debug("Docker is installed!")
    else:
        user_logger.error("/!\\ ERROR: Docker is not installed!")
        exit(-1)

    if check_docker_daemon():
        if logger.isEnabledFor(DEBUG):
            logger.debug("Docker daemon is running!")
    else:
        user_logger.error("/!\\ ERROR: Docker daemon is not running!")
        exit(-1)

    # Check image exists
    if not check_local_image(platform.docker_image):
        user_logger.info(f"Image {platform.docker_image} does not exist!, pull the image first.")
        result = pull_docker_image(platform.docker_image)
        if not result:
            user_logger.error(f"/!\\ ERROR: Failed to pull image {platform.docker_image}.")
            exit(-1)

    running_status = False
    container_id = None
    container_match = check_running_container(platform, all=all)
    if len(container_match) > 0:
        container_running = [container for status, container in container_match if status == 'running']
        container_stopped = [container for status, container in container_match if status != 'running']

        if len(container_running) > 0:
            # Get the first container
            running_status = True
            container_id = container_running[0].short_id
            if logger.isEnabledFor(DEBUG):
                logger.debug(f"Found running container {container_id}.")

            if platform.force_start:
                if logger.isEnabledFor(DEBUG):
                    logger.debug(f"Per request force_start=True, will re-start the container.")
                    logger.debug(f"Stop all containers {container_match}")
                stop_all_containers_2(container_match)
                container_id = None
        else:
            if logger.isEnabledFor(DEBUG):
                logger.debug(f"Found stopped container {container_stopped[0].short_id}.")
            # Get the first container
            container = container_stopped[0]
            container.restart()
            container_id = container.short_id

    if container_id is None:
        # Start the container
        if logger.isEnabledFor(DEBUG):
            logger.debug(f"Start container: {platform.docker_image}!")
        container_id = platform.start_container(**kwargs)

    return container_id


# TODO: not used and got replaced
def verify_mount(container, platform):
    # TODO: currently only check job_directory exists in the mounts. Is it enough?
    directory = platform.job_directory
    mounts = container.attrs['Mounts']  # list
    mount_bindings = {}
    for mount in mounts:
        mount_bindings[mount['Source']] = mount['Destination']
    # normalize directory and mount paths
    directory = directory.replace("\\", '/')
    mounts = {k.replace("\\", '/'): v.replace("\\", '/') for k, v in mount_bindings.items()}
    if directory in mounts:
        if logger.isEnabledFor(DEBUG):
            logger.debug("Mount verified.")
        return True
    else:
        if logger.isEnabledFor(DEBUG):
            logger.debug("Mount not verified.")
            logger.debug("The running container has the following mounts:\n")
            logger.debug(json.dumps(mounts, indent=3))
        return False


#############################
## Check containers
#############################

def find_container_by_image(image: str, all: bool = False) -> Dict:
    client = docker.from_env()
    container_found = {}
    for container in client.containers.list(all=all):
        if image in container.image.tags:
            if logger.isEnabledFor(DEBUG):
                logger.debug(f"Image {image} found in container: {container.short_id}")
            if container_found.get(container.status, None) is None:
                container_found[container.status] = []
            container_found[container.status].append(container)

    return container_found


def find_container_by_image_bk(image: str, all: bool = False) -> List:
    client = docker.from_env()
    container_found = []
    for container in client.containers.list(all=all):
        if image in container.image.tags:
            if logger.isEnabledFor(DEBUG):
                logger.debug(f"Image {image} found in container: {container.short_id}")
            container_found.append(container)

    return container_found


def check_running_container(platform, image: str = None, all: bool = False) -> Any:
    if image is None:
        image = platform.docker_image
    container_found = find_container_by_image(image, all)
    container_match = []
    if len(container_found) > 0:
        for status, containers in container_found.items():
            # if verify_mount(container, platform):
            #     return container.id
            for container in containers:
                if platform.compare_mounts(container):
                    if logger.isEnabledFor(DEBUG):
                        logger.debug(f"Found match mounts container {container.short_id}.")
                    container_match.append((status, container))

        if len(container_match) == 0:
            if logger.isEnabledFor(DEBUG):
                logger.debug(f"Found container with image {image}, but no one match platform mounts.")
    else:
        if logger.isEnabledFor(DEBUG):
            logger.debug(f"Not found container matching image {image}.")

    return container_match


def stop_all_containers(image: str):
    client = docker.from_env()
    for container in client.containers.list():
        if image in container.image.tags:
            container.stop()
            container.remove()


def stop_all_containers_2(containers: List):
    for container in containers:
        container.stop()
        container.remove()


def stop_container(container_id):
    client = docker.from_env()
    container = client.containers.get(container_id)
    container.stop()
    container.remove()


#############################
## Check docker
#############################

def is_docker_installed():
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


def check_docker_daemon():
    try:
        client = docker.from_env()
        client.ping()
        if logger.isEnabledFor(DEBUG):
            logger.debug("Docker daemon is running.")
        return True
    except docker.errors.APIError as e:
        if logger.isEnabledFor(DEBUG):
            logger.debug("Docker daemon is not running:", e)
        return False
    except Exception as ex:
        if logger.isEnabledFor(DEBUG):
            logger.debug("Error checking Docker daemon:", ex)
        return False


#############################
## Check images
#############################

def check_local_image(image_name: str):
    client = docker.from_env()
    for image in client.images.list():
        if image_name in image.tags:
            return True
    return False


def pull_docker_image(image_name, tag='latest'):
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
    except docker.errors.APIError as e:
        if logger.isEnabledFor(DEBUG):
            logger.debug(f'Error pulling {full_image_name}: {e}')
        return False

