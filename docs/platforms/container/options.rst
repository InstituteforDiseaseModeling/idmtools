.. _options:

==========================
Container Platform Options
==========================
|IT_s| supports the |CONTAINER_s| platform options for configuring, submitting, and running jobs.
The following lists some of the |CONTAINER_s| platform options
that are used when making calls to :py:class:`idmtools_platform_container.container_platform.ContainerPlatform`.

* docker_image: The docker image to use for the job
* extra_packages: A list of extra packages to install in the container
* retries: The number of retries to attempt for a job
* data_mount: The data mount to use for mounting data for job directory into the container
* user_mounts: A list of user mounts to use for mounting user directories into the container
* container_prefix: The prefix to use for the container name
* force_start: Whether to force start the stopped or running container
* new_container: Whether to create a new container
* include_stopped: Whether to reuse a stopped container
* debug: Whether to run the container in debug mode

Following example shows how to use the |CONTAINER_s| platform option with extra_packages:

.. literalinclude:: ../../../examples/platform_container/extra_packages.py


