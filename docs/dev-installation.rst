======================
Developer installation
======================

Follow the steps below if you will make changes to the |IT_s| source code to add new functionality.

Install |IT_s|
==============

#.  Install a Git client such as Git Bash or the Git GUI.
#.  Open a command prompt and clone the |IT_s| GitHub repository to a local directory using the following command::

        git clone https://github.com/InstituteforDiseaseModeling/idmtools.git

        To work from the latest approved code, work from the "master" branch. To work from
        the latest code under active development, work from the "dev" branch.

#.  Open a command prompt and create a virtual environment in any directory you choose. The
    command below names the environment "idmtools", but you may use any desired name::

        python -m venv idmtools

#.  Activate the virtual environment:

        * On Windows, enter the following::

            idmtools\Scripts\activate

        * On Linux, enter the following::

            source idmtools/bin/activate

#.  In the base directory of the cloned GitHub repository, run the setup script.

        * On Windows, enter the following::

            pip install py-make
            pymake setup-dev

        * On Linux, enter the following::

            make setup-dev

#.  To verify that |IT_s| is installed, enter the following command::

        idmtools --help

    You should see a list of available cookie cutter projects and command-line options.

#.  For source completion and indexing, set the package paths in your IDE. In PyCharm, select
    the following directories then right-click and select **Mark Directory as** > **Source Root**.

    - idmtools/idmtools_core
    - idmtools/idmtools_cli
    - idmtools/idmtools_platform_local
    - idmtools/idmtools_platform_comps
    - idmtools/idmtools_model_emod
    - idmtools/idmtools_models
    - idmtools/idmtools_test

.. TBD add a link to the CLI reference when complete

.. _docker-client:

Start the Docker client
=======================

#.  Create a Docker network named idmtools_network in the idmtools_local_runner directory using the
    following commands::

        cd idmtools_platform_local
        docker network create idmtools_network

    .. note::

        The drive where you create the network most be shared with Docker. Open Docker and then under **Settings > Shared Drives**, verify that the drive is shared.

#.  Start the local Docker runner using the following commands, depending on your operating system.

    * On Windows, enter the following. Include the first line only if the data/redis-data directory
      is not already present::

        mkdir data\redis-data
        docker-compose down -v
        docker-compose build
        docker-compose up -d

    * On Linux, enter the following::

        sudo docker-compose down -v
        sudo docker-compose build
        sudo ./start.sh

#.  Open a browser and navigate to http://localhost:5000/data/.

.. note::

    If your password has changed since running Docker, you will need to update
    your credentials. Open Docker Desktop > Settings > Resources > File sharing and reset
    your credentials.

Run tests
=========

If you want to run tests on the code, do the following. You can add new tests
to the GitHub repository and they will be run using the same commands. Note
that |COMPS_s| access is generally restricted to |IDM_s| employees.

#.  Login to |COMPS_s| by navigating to the |IT_s| root directory and entering the following
    at a command prompt::

        python dev_scripts\create_auth_token_args.py --comps_url https://comps2.idmod.org --username yourcomps_user --password yourcomps_password

#.  If you are running the local platform with the nightly |IT_s| build, enter the following
    to log in to Docker::

        docker login idm-docker-staging.packages.idmod.org

#.  Navigate to the directory containing the code you want  to test, such as
    the root directory or a subdirectory like idmtools_platform_comps, enter the
    following command::

        pymake test-all







