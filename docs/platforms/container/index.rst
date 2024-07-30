=========
CONTAINER
=========

.. toctree::
    :maxdepth: 2

    options
    cancel
    docker_image

The |CONTAINER_s| platform allows use of the |CONTAINER_l| on local host along with docker container.
This platform facilitates the submission of jobs to a Docker container. Functioning as a wrapper around the file
platform, it constructs simulation job directory structures on the local host and then dispatches these files to a
Docker container for execution. Consequently, the Docker image used for running simulations only needs to have MPI and
Python 3.9 installed for EMOD simulations. Any additional requirements for the simulation should be incorporated into
the host’s virtual environment. The Container platform automatically mounts the job directory, created on the host
machine, to the Docker container. It also can dynamically install required packages into container. For more details on
the architecture and the packages included in |IT_s| and |CONTAINER_s|, please refer to the documentation
(:doc:`../../reference`).


Prerequisites
=============
* Docker installed
* Linux or Windows with WSL2
* |Python_IT| (https://www.python.org/downloads/release)
* Python virtual environments

    Python virtual environments enable you to isolate your Python environments from one
    another and give you the option to run multiple versions of Python on the same computer. When using a
    virtual environment, you can indicate the version of Python you want to use and the packages you
    want to install, which will remain separate from other Python environments. You may use
    ``virtualenv``, which requires a separate installation, but ``venv`` is recommended and included with Python 3.8+.

Configuration
=============
The |CONTAINER_s| platform requires to provide some configuration elements to define its operation.

You can define these parameters in your ``idmtools.ini`` file by adding a configuration block for Slurm.


  idmtools.ini example::

    [CONTAINER]
    type = Container
    job_directory = /home/userxyz/any_directory_for_suite


You can also do this directly from code by passing the minimum requirements
  Python script example::

    Platform('Container', job_directory='/home/userxyz/any_directory_for_suite')



Configuration Options
`````````````````````
.. list-table:: Title
   :header-rows: 1

   * - Parameter
     - Description
   * - **job_directory**
     - This defines the location that |IT_s| will use to manage experiments on the |CONTAINER_s| platform. The directory should be located somewhere in your local host.
   * - docker_image
     - The docker image to use for the simulation. This is optional, and if not provided, the default image docker-production-public.packages.idmod.org/idmtools/container-rocky-runtime:0.0.1 will be used which will be pulled from idmtools docker public artifactory at first time.
   * - other options:
     - Other options can be passed Platform, please see documentation about the :ref:`Container Platform options <options>`.

.. note::

    Bold parameters are required



Recommendations
===============

* Simulation results and files should be backed up

Getting started
===============
After you have installed |IT_s| (:doc:`../../basic-installation` or :doc:`../../dev-installation`) and met the
above listed prerequisites, you can begin submitting and running jobs to your |CONTAINER_s| with |IT_s|.

Verify docker is running
````````````````````````````````````
Type the following at a terminal session to verify that docker is running::

    docker info
    docker version

This will provide Docker's current status or an error message if Docker is not running.


Submit a job
````````````
Run the following included Python example to submit and run a job on your |CONTAINER_s| platform:

.. literalinclude:: ../../../examples/platform_container/python_sims_for_containerplatform.py

.. note::

    ``workitems`` and ``AssetCollection`` are not supported on the |CONTAINER_s| platform with |IT_s|. If you've
    used the |COMPS_s| platform with |IT_s| you may have scripts using these objects. You would need
    to update these scripts without using these objects in order to run them on the |CONTAINER_s| platform.


