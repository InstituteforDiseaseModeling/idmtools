import uuid
import docker
import requests
from idmtools_platform_container.container_operations.docker_operations import stop_container

client = docker.from_env()


def find_containers_by_prefix(prefix, image_name=None):
    # List all containers, including non-running ones
    containers = client.containers.list(all=True)
    matched_containers = []

    # Iterate through containers to find matches
    for container in containers:
        # Container names in Docker are prefixed with '/', so we need to strip that
        container_name = container.name.lstrip('/')
        if container.status == 'running':
            try:
                if image_name in container.image.tags or image_name is None:
                    if container_name.startswith(prefix):
                        matched_containers.append(container_name)
            except requests.exceptions.HTTPError as e:
                print(f"An error occurred: {e}")

    return matched_containers


def is_valid_container_name_with_prefix(container_name, prefix):
    # Check if the container name starts with the prefix
    if not container_name.startswith(prefix):
        return False

    potential_uuid = container_name[len(prefix):][1:]

    try:
        uuid.UUID(potential_uuid, version=4)
    except ValueError:
        return False
    return True


def find_containers_by_image_prefix(image_prefix):
    # List all containers, including non-running ones
    containers = client.containers.list(all=True)
    matched_containers = []

    # Iterate through containers to find matches
    for container in containers:
        container_name = container.name.lstrip('/')
        # Check if the container is running
        if container.status == 'running':
            try:
                # Check if any of the container's image tags start with the image prefix
                if any(tag.startswith(image_prefix) for tag in container.image.tags):
                    matched_containers.append(container_name)
            except requests.exceptions.HTTPError as e:
                print(f"An error occurred: {e}")

    return matched_containers


def delete_containers_by_image_prefix(image_prefix):
    # Find containers whose image name starts with the given prefix
    containers_to_delete = find_containers_by_image_prefix(image_prefix)

    # Delete each matched container
    for container_name in containers_to_delete:
        stop_container(container_name, remove=True)


def get_container_name_by_id(container_id):
    client = docker.from_env()
    try:
        container = client.containers.get(container_id)
        return container.name
    except docker.errors.NotFound:
        print(f"Container with ID {container_id} does not exist.")
    except docker.errors.APIError as e:
        print(f"An error occurred: {e}")


def get_container_status_by_id(container_id):
    try:
        container = client.containers.get(container_id)
        return container.status
    except docker.errors.NotFound:
        print(f"Container with ID {container_id} does not exist.")
    except docker.errors.APIError as e:
        print(f"An error occurred: {e}")