ContainerPlatform Docker utilities
==================================

The `docker_operations.py` module provides various utilities to manage Docker containers within the `ContainerPlatform`. These utilities include functions to validate, start, stop, and manage Docker containers, as well as to check Docker installation and daemon status.

Key functions
-------------

- **validate\_container\_running(platform, \*\*kwargs)**: Checks if the Docker daemon is running, finds an existing container, or starts a new container.
- **get\_container(container\_id)**: Retrieves the container object by container ID.
- **find\_container\_by\_image(image, include\_stopped=False)**: Finds containers that match the specified image.
- **stop\_container(container, remove=True)**: Stops a container and optionally removes it.
- **stop\_all\_containers(containers, keep\_running=True, remove=True)**: Stops all specified containers.
- **restart\_container(container)**: Restarts a container.
- **sort\_containers\_by\_start(containers, reverse=True)**: Sorts containers by their start time.
- **get\_containers(include\_stopped=False)**: Retrieves all containers, optionally including stopped ones.
- **get\_working\_containers(container\_id=None, entity=False)**: Retrieves working containers.
- **is\_docker\_installed()**: Checks if Docker is installed.
- **is\_docker\_daemon\_running()**: Checks if the Docker daemon is running.
- **check\_local\_image(image\_name)**: Checks if the specified Docker image exists locally.
- **pull\_docker\_image(image\_name, tag='latest')**: Pulls a Docker image from the repository.
- **compare\_mounts(mounts1, mounts2)**: Compares two sets of mount configurations.
- **compare\_container\_mount(container1, container2)**: Compares the mount configurations of two containers.
- **list\_running\_jobs(container\_id, limit=None)**: Lists all running jobs on the specified container.
- **find\_running\_job(item\_id, container\_id=None)**: Finds a running job by item ID and optionally container ID.

Usage
-----

These utilities are typically used to manage Docker containers within the `ContainerPlatform`, ensuring that the necessary containers are running and properly configured for executing experiments and simulations.

Example
-------

.. code-block:: python

    from idmtools_platform_container.container_operations.docker_operations import (
        validate_container_running, get_container, stop_container
    )

    # Validate and start a container
    container_id = validate_container_running(platform)

    # Retrieve a container object
    container = get_container(container_id)

    # Stop a container
    stop_container(container)