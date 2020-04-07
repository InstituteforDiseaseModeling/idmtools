==================
Basic installation
==================

Follow the steps below if you will use |IT_s| to run and analyze simulations, but will not make
source code changes.

#.  Open a command prompt and create a virtual environment in any directory you choose. The
    command below names the environment "idmtools", but you may use any desired name::

        python -m venv idmtools

#.  Activate the virtual environment:

        * On Windows, enter the following::

            idmtools\Scripts\activate

        * On Linux, enter the following::

            source idmtools/bin/activate

#.  Install |IT_s| packages::

        pip install idmtools[idm] --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple

    If you are on Python 3.6, also run::

        pip install dataclasses

#.  Verify installation by pulling up |IT_s| help::

        idmtools --help

#.  When you are finished, deactivate the virtual environment by entering the following at a command prompt::

        deactivate

