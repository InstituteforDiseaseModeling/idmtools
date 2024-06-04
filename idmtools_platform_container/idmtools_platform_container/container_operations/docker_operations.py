from typing import Any
import json
import docker
from logging import getLogger

user_logger = getLogger('user')


def ensure_docker_daemon_running(platform, **kwargs):
    """
    Check if the docker daemon is running and start it if it is not running.
    Args:
        platform: Platform
        kwargs: additional arguments
    Returns:
        Container ID
    """
    if check_docker_daemon():
        user_logger.debug("Docker daemon is running!")
    else:
        user_logger.error("/!\\ ERROR: Docker daemon is not running!")
        exit(-1)

    # Check image exists
    if not check_image(platform.docker_image):
        user_logger.error(
            f"/!\\ ERROR: Image {platform.docker_image} does not exist!, please build or pull the image first.")
        exit(-1)

    container_id = check_container_running(platform.docker_image, platform)
    if container_id is not None or platform.force_start:
        user_logger.debug("Docker container is already running!")
        user_logger.debug(f"Stop all containers {platform.docker_image}!")
        stop_all_containers(platform.docker_image)
        container_id = None

    if container_id is None:
        if check_container_name(platform.container_name):
            user_logger.error(f"Container name '{platform.container_name}' is already being used!")
            if platform.force_start:
                user_logger.debug(f"Stop container '{platform.container_name}'!")
                stop_container(platform.container_name)
            else:
                user_logger.error("Please provide a different container name or set force_start to True.")
                exit(-1)

        # restart the container
        user_logger.debug(f"Start container: {platform.docker_image}!")
        container_id = platform.start_container(**kwargs)

    return container_id


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
        print("Mount verified.")
        return True
    else:
        print("Mount not verified.")
        # print("The cunning container has the following mounts:\n", mounts)
        print("The cunning container has the following mounts:\n")
        print(json.dumps(mounts, indent=3))
        return False


def check_container_running(image: str, platform) -> Any:
    # TODO: should or can we check container name?
    client = docker.from_env()
    for container in client.containers.list():
        if container.image.tags[0] == image:
            print("Container is running.")
            if verify_mount(container, platform):
                return container.id
            else:
                print(
                    f"Platform job_directory '{platform.job_directory}' is different from being used in the running container, please modify job_directory or re-start the container.")
                # exit(-1)
                return None
    print("Container is not running.")
    return None


def check_container_name(container_name: str) -> Any:
    # TODO: should or can we check container name?
    client = docker.from_env()
    for container in client.containers.list():
        if container.name == container_name:
            print(f"Container name {container_name} is being used.")
            return True

    print(f"Container name {container_name} is not being used.")
    return False


def stop_all_containers(image: str):
    client = docker.from_env()
    for container in client.containers.list():
        if container.image.tags[0] == image:
            container.stop()
            container.remove()


def stop_container(container_id):
    client = docker.from_env()
    container = client.containers.get(container_id)
    container.stop()
    container.remove()


def check_docker_daemon():
    try:
        client = docker.from_env()
        client.ping()
        print("Docker daemon is running.")
        return True
    except docker.errors.APIError as e:
        print("Docker daemon is not running:", e)
        return False
    except Exception as ex:
        print("Error checking Docker daemon:", ex)
        return False


def check_image(image_name: str):
    client = docker.from_env()
    for image in client.images.list():
        if image_name in image.tags:
            return True
    return False


def list_images():
    client = docker.from_env()
    return client.images.list()
