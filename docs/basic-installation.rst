==================
Basic installation
==================

Follow the steps below if you will use |IT_s| to run and analyze simulations, but will not make
source code changes.

#.  Open a command prompt and create a virtual environment in any directory you choose. The
    command below names the environment "idmtools", but you may use any desired name::

        python -m venv idmtools

#.  Activate the virtual environment:

    * For Windows, enter the following::

        idmtools\Scripts\activate

    * For Linux, enter the following::

        source idmtools/bin/activate

#.  Install |IT_s| packages::

        pip install idmtools[idm] --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple

    .. note::

        When reinstalling |IT_s| you should use the ``--no-cache-dir`` and ``--force-reinstall`` options, such as: ``pip install idmtools[idm] --index-url=https://packages.idmod.org/api/pypi/pipi-production/simple --no-cache-dir --force-reinstall``. Otherwise, you may see the error, **idmtools not found**, when attempting to open and run one of the example Python scripts.

#.  Verify installation by pulling up |IT_s| help::

        idmtools --help

#.  When you are finished, deactivate the virtual environment by entering the following at a command prompt::

        deactivate

