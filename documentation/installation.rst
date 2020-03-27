============
Installation
============

You can install |IT_l| in two different ways. If you intend to use |IT_s| as |IDM_s| builds it,
follow the instructions in :ref:`tools-basic`. However, if you intend to modify the |IT_s| source
code to add new functionality, follow the instructions in :ref:`tools-dev`. Whichever installation
method you choose, the prerequisites are the same. 

Prerequisites
=============

|IT_s| uses Docker to run |IT_s| within a container to keep the |IT_s| environment securely
isolated. You must also have |Python_IT| and Python virtual environments installed to isolate your
|IT_s| installation in a separate Python environment. If you do not already have these installed,
see the links below for instructions. 

* Docker (https://docs.docker.com/)
* |Python_IT| (https://www.python.org/downloads/release)
* Python virtual environments (https://virtualenv.pypa.io/en/stable/installation/)


.. _tools-basic:

Basic installation
===================

Follow the steps below if you will use |IT_s| to run and analyze simulations, but will not make
source code changes. 

TBD after pip installation from Artifactory is complete 

.. _tools-dev:

Developer installation
======================

Follow the steps below if you will make changes to the |IT_s| source code to add new functionality. 

#.  Install a Git client such as Git Bash or the Git GUI.
#.  Open a command prompt and clone the |IT_s| GitHub repository using the following command::
        
        git clone https://github.com/InstituteforDiseaseModeling/idmtools.git

#.  Add the following paths to your PYTHONPATH environment variable, prepending each with the full 
    path to the GitHub clone::

        idmtools/idmtools_core
        idmtools/idmtools_local_runner
        idmtools/idmtools_models_collection

#.  Navigate to the root directory or anywhere else you want to create your virtual environment::

        cd idmtools

#.  Create a virtual environment called "idmtools" or other desired name in which to install |IT_s|::

        virtualenv idmtools

#.  Activate the environment using one of the following commands, depending on your operating system. 
    
    * On Windows::

        idmtools\Scripts\activate

    * On Linux::

        source idmtools/bin/activate

#.  If you want to run tests on the code, enter the following commands to install extra test dependencies::


        cd idmtools_core
        pip install -e .[test] --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple
        cd ../idmtools_local_runner
        pip install -e .[test]
        cd ../idmtools_models_collection
        pip install -e .[test]

#.  Create a Docker network named idmtools_network in the idmtools_local_runner directory using the 
    following commands::

        cd ../idmtools_local_runner
        docker network create idmtools_network

    .. note::

        The drive where you create the network most be shared with Docker. Open **Settings > Shared Drives**
        and verify that the drive is shared.

#.  Start the local Docker runner using the following commands, depending on your operating system.

    * On Windows, enter the following. Include the first line only if the data/redis-data directory 
      is not already present::

        mkdir data\\redis-data
        docker-compose down -v
        docker-compose build
        docker-compose up -d

    * On Linux, enter the following::

        sudo docker-compose down -v
        sudo docker-compose build
        sudo ./start.sh

    You can now open a browser and navigate to http://localhost:5000/data/.

