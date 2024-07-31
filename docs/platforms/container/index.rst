.. _Container Platform:

==================
Container Platform
==================

.. toctree::
    :maxdepth: 1

    utilis
    options
    docker_image

Prerequisites
-------------
* Docker installed
* Linux or Windows with WSL2
* |Python_IT| (https://www.python.org/downloads/release)
* Python virtual environments

    Python virtual environments enable you to isolate your Python environments from one
    another and give you the option to run multiple versions of Python on the same computer. When using a
    virtual environment, you can indicate the version of Python you want to use and the packages you
    want to install, which will remain separate from other Python environments. You may use
    ``virtualenv``, which requires a separate installation, but ``venv`` is recommended and included with Python 3.8+.

ContainerPlatform
-----------------

The **ContainerPlatform** class is a part of the |IT_s| platform. This platform leverages Docker's containerization capabilities to provide a consistent and isolated environment for running computational tasks. The **ContainerPlatform** is responsible for managing the creation, execution, and cleanup of Docker containers used to run simulations. It offers a high-level interface for interacting with Docker containers, allowing users to submit jobs, monitor their progress, and retrieve results.
For more details on the architecture and the packages included in |IT_s| and **ContainerPlatform**, please refer to the documentation
(:doc:`../../reference`).

Key Features
------------

- **Docker Integration**: Ensures that Docker is installed and the Docker daemon is running before executing any tasks.
- **Experiment and Simulation Management**: Provides methods to run and manage experiments and simulations within Docker containers.
- **Volume Binding**: Supports binding host directories to container directories, allowing for data sharing between the host and the container.
- **Container Validation**: Validates the status and configuration of Docker containers to ensure they meet the platform's requirements.
- **Script Conversion**: Converts scripts to Linux format if the host platform is Windows, ensuring compatibility within the container environment.
- **Job History Management**: Keeps track of job submissions and their corresponding container IDs for easy reference and management.

.. _attributes:

Attributes
----------

- **job\_directory**: The directory where job data is stored.
- **docker\_image**: The Docker image to run the container.
- **extra_\packages**: Additional packages to install in the container.
- **data\_mount**: The data mount point in the container.
- **user\_mounts**: User-defined mounts for additional volume bindings.
- **container\_prefix**: Prefix for container names.
- **force\_start**: Flag to force start a new container.
- **new\_container**: Flag to start a new container.
- **include\_stopped**: Flag to include stopped containers in operations.
- **debug**: Flag to enable debug mode.
- **container\_id**: The ID of the container being used.
- **max\_job**: The maximum number of jobs to run in parallel.
- **retries**: The number of retries to attempt for a job.

Usage
-----

The `ContainerPlatform` class is typically used to run computational experiments and simulations within Docker containers, ensuring a consistent and isolated environment. It provides various methods to manage and validate containers, submit jobs, and handle data volumes.

Example
-------

.. code-block:: python

    from idmtools_platform_container.container_platform import ContainerPlatform

    # Initialize the platform
    platform = ContainerPlatform(job_directory="destination_directory")
    # OR
    # Platform('Container', job_directory='destination_directory')

    # Define task
    command = "echo 'Hello, World!'"
    task = CommandTask(command=command)
    # Run an experiment
    experiment = Experiment.from_task(task, name="example")
    experiment.run(platform=platform)


More Examples
-------------
Run the following included Python example to submit and run a job on your |CONTAINER_s| platform:

.. literalinclude:: ../../../examples/platform_container/python_sims_for_containerplatform.py

.. note::

    ``workitems`` and ``AssetCollection`` are not supported on the |CONTAINER_s| platform with |IT_s|. If you've
    used the |COMPS_s| platform with |IT_s| you may have scripts using these objects. You would need
    to update these scripts without using these objects in order to run them on the |CONTAINER_s| platform.


