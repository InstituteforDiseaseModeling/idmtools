"""
Here we implement the ContainerPlatform docker operations.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import docker
import platform as sys_platform
import subprocess
from dataclasses import dataclass, field
from typing import List, Dict, NoReturn, Any, Union
from idmtools.core import ItemType
from idmtools_platform_container.utils.general import normalize_path, parse_iso8601
from idmtools_platform_container.utils.job_history import JobHistory
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
            container = get_container(container_id)
            if sys_platform.system() not in ["Windows"]:
                command = f"bash -c '[ \"$(ls -lart {platform.data_mount} | wc -l)\" -ge 3 ] && echo exists || echo not_exists'"
                result = container.exec_run(command)
                output = result.output.decode().strip()
                if output == "not_exists":
                    stop_container(container_id, remove=True)
                    if logger.isEnabledFor(DEBUG):
                        logger.debug(f"Existing container {container_id} is not usable")
                    container_id = None

            if container_id is not None:
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
        logger.debug(f"Container with ID {container_id} not found.")
        return None
    except DockerAPIError as e:
        logger.debug(f"Error retrieving container with ID {container_id}: {str(e)}")
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
    container_found = {}
    for status, container_list in get_containers(include_stopped).items():
        container_found[status] = [container for container in container_list if
                                   image == container.attrs['Config']['Image']]

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
        exit(-1)
    except DockerAPIError as e:
        logger.debug(f"Error stopping container {str(container)}: {str(e)}")
        exit(-1)


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


def restart_container(container: Union[str, Container]) -> NoReturn:
    """
    Restart a container.
    Args:
        container: container id or container object to be restarted
    Returns:
        No return
    """
    try:
        if isinstance(container, str):
            container = get_container(container)
        elif not isinstance(container, Container):
            raise TypeError("Invalid container object.")

        if container is None:
            user_logger.error(f"Container {container} not found.")
            exit(-1)

        # Restart the container
        container.restart()
        if logger.isEnabledFor(DEBUG):
            logger.debug(f"Container {container.short_id} has been restarted.")
    except DockerAPIError as e:
        user_logger.error(f"Error restarting container {container.short_id}: {str(e)}")
        exit(-1)
    except Exception as e:
        user_logger.error(f"Restarting container {container.short_id} encounters an unexpected error: {e}")
        exit(-1)


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


def get_containers(include_stopped: bool = False) -> Dict:
    """
    Find the containers that match the image.
    Args:
        include_stopped: bool, if consider the stopped containers or not
    Returns:
        dict of containers
    """
    client = docker.from_env()
    container_found = {}
    # Get all containers
    all_containers = client.containers.list(all=include_stopped)
    # Filter the containers
    all_containers = [ct for ct in all_containers if
                      ct.status in CONTAINER_STATUS and JobHistory.verify_container(ct.short_id)]
    # Separate the containers
    container_found['running'] = [ct for ct in all_containers if ct.status == 'running']
    container_found['stopped'] = [ct for ct in all_containers if ct.status != 'running']

    return container_found


def get_working_containers(container_id: str = None, entity: bool = False) -> List[Any]:
    """
    Get the working containers.
    Args:
        container_id: Container ID
        entity: bool, if return the container object or container id
    Returns:
        list of working containers or IDs
    """
    if container_id is None:
        if entity:
            containers = get_containers().get('running', [])
        else:
            containers = [c.short_id for c in get_containers().get('running', [])]
    else:
        # Check if the container is in the history and running
        if not JobHistory.verify_container(container_id):
            # The container is not in the history.
            logger.error(f"Container {container_id} not found in History.")
            containers = []
        else:
            # The container is in the history, we need to verify if it still exists.
            container = get_container(container_id)
            if container:
                # We only consider the running container
                if container.status == 'running':
                    containers = [container] if entity else [container.short_id]
                else:
                    logger.warning(f"Container {container_id} is not running.")
                    containers = []
            else:
                logger.warning(f"Container {container_id} not found.")
                containers = []

    return containers


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
    # Check if the image name contains the tag
    if ':' in image_name:
        full_image_name = image_name
    else:
        full_image_name = f'{image_name}:{tag}'

    # Pull the image
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


def compare_container_mount(container1: Union[str, Container], container2: Union[str, Container]) -> bool:
    """
    Compare the mount configurations of two containers.
    Args:
        container1: container object or id
        container2: container object or id
    Returns:
        True/False
    """
    # Get the container objects
    if isinstance(container1, str):
        container1 = get_container(container1)

    if isinstance(container2, str):
        container2 = get_container(container2)

    # Get the mount configurations
    mounts1 = container1.attrs['Mounts']
    mounts2 = container2.attrs['Mounts']

    return compare_mounts(mounts1, mounts2)


#############################
# Check jobs
#############################

PS_QUERY = 'ps xao pid,ppid,pgid,etime,cmd | head -n 1 && ps xao pid,ppid,pgid,etime,cmd | grep -e EXPERIMENT -e SIMULATION | grep -v grep'


@dataclass(repr=False)
class Job:
    """Running Job."""
    item_id: str = field(init=True)
    item_type: str = field(init=True)
    job_id: int = field(init=True)
    group_pid: int = field(init=True)
    container_id: str = field(init=True)
    elapsed: str = field(init=True)
    parent_pid: int = field(default=None, init=True)

    def display(self):
        """Display Job for debugging usage."""
        user_logger.info(f"Item ID: {self.item_id:15}")
        user_logger.info(f"Item Type: {self.item_type:15}")
        user_logger.info(f"Job ID: {self.job_id:15}")
        user_logger.info(f"Group PID: {self.group_pid:15}")
        user_logger.info(f"Container ID: {self.container_id:15}")
        user_logger.info(f"Elapsed: {self.elapsed:15}")


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
        processes = result.stdout.splitlines()
        header = processes[0].split()  # Extract the header (column names)
        for line in processes[1:]:  # Skip the first header line
            if 'EXPERIMENT' in line or 'SIMULATION' in line:
                # Split the line into columns
                columns = line.split(maxsplit=len(header) - 1)
                # Convert columns to their respective types
                pid = int(columns[0])  # pid is an integer
                ppid = int(columns[1])  # ppid is an integer
                pgid = int(columns[2])  # pgid is an integer
                etime = columns[3]  # etime is a string
                cmd = columns[4]  # cmd is a string

                # Determine the item type and job ID
                item_type = ItemType.EXPERIMENT if 'EXPERIMENT' in cmd else ItemType.SIMULATION
                job_id = pgid if 'EXPERIMENT' in cmd else pid

                # Find the item that starts with 'EXPERIMENT' or 'SIMULATION'
                columns = cmd.split()
                result = [item for item in columns if item.startswith('EXPERIMENT') or item.startswith('SIMULATION')]
                item_id = result[0].split(':')[1]

                # Create a new job
                job = Job(item_id=item_id, item_type=item_type, job_id=job_id, group_pid=pgid, parent_pid=ppid,
                          container_id=container_id, elapsed=etime)
                running_jobs.append(job)
    elif result.returncode == 1:
        pass
    else:
        logger.error(result.stderr)
        user_logger.error(f"Command failed with return code {result.returncode}")
        exit(-1)

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
        # Check if the item is an Experiment ID
        his_job = JobHistory.get_job(item_id)
        if his_job:
            # item_id is an Experiment ID
            containers = [his_job['CONTAINER']]
        else:
            # item_id is a Simulation ID or Job ID, we need to check all working containers
            containers = get_working_containers()

    match_jobs = []
    for cid in containers:
        # List all running jobs on the container
        jobs = list_running_jobs(cid)
        if len(jobs) == 0:
            continue

        # Container has running jobs
        for job in jobs:
            # Check if the job is the one we are looking for
            if job.item_id == item_id or str(job.job_id) == str(item_id):
                match_jobs.append(job)
                break  # One running container can't have multiple matches!

    if len(match_jobs) > 1:
        # item_id must be a Job ID in this case and container_id must be None!
        user_logger.error(
            f"Multiple jobs found for Job ID {item_id}, please provide the Container ID or use Entity ID instead.")
        exit(-1)
    elif len(match_jobs) == 1:
        return match_jobs[0]
    else:
        return None
