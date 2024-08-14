======================
Container CLI commands
======================

This document provides an overview of the CLI(command-line interface) commands available for the container platform.

.. contents:: Table of Contents
   :depth: 2
   :local:

Introduction
------------

The Container platform CLI provides a set of commands to manage and interact with containers. These commands allow you to verify the Docker environment, manage experiments and simulations, and inspect containers.

Command list
------------

**Main commands**:

- `cancel`:  Cancel an Experiment/Simulation job.
- `history`: View the job history.
- `jobs`: List running Experiment/Simulation jobs.
- `status`: Check the status of an Experiment/Simulation.

**Rest of the commands**:

- `verify-docker`: Verify the Docker environment.
- `get-detail`: Retrieve Experiment history.
- `path`: Locate Suite/Experiment/Simulation file directory.
- `is-running`: Check if an Experiment/Simulation is running.
- `volume`: Check the history volume.
- `clear-history`: Clear the job history.
- `sync-history`: Sync the file system with job history.
- `history-count`: Get the count of job histories.
- `clear-results`: Clear job results files and folders.
- `inspect`: Inspect a container.
- `stop-container`: Stop running container(s).
- `remove-container`: Remove stopped containers.
- `install`: Pip install a package on a container.
- `packages`: List packages installed on a container.
- `ps`: List running processes in a container.
- `list-containers`: List all available containers.
- `match-container`: List matched containers.
- `inspect-image`: Inspect a container image.
- `parameters`: List parameter info for a platform.

Detailed command descriptions
-----------------------------

cancel
^^^^^^

**Usage**: `idmtools container cancel ITEM_ID [-c CONTAINER_ID]`

**Arguments**:

- `ITEM_ID`: Experiment/Simulation ID or Job ID (required)
- `-c, --container_id`: Container ID (optional)

**Description**: Cancel an Experiment/Simulation job.

**Examples**:

.. code-block:: bash

   $ idmtools container cancel 6f305619-64b3-ea11-a2c6-c4346bcb1557
   $ idmtools container cancel 12345
   $ idmtools container cancel 12345 -c my_container


history
^^^^^^^

**Usage**: `idmtools container history [CONTAINER_ID] [-l LIMIT] [-n NEXT]`

**Arguments**:

- `CONTAINER_ID`: Container ID (optional)
- `-l, --limit`: Max number of jobs to show (default: 10)
- `-n, --next`: Next number of jobs to show (default: 0)

**Description**: View job history.

**Examples**:

.. code-block:: bash

   $ idmtools container history
   $ idmtools container history my_container -l 5 -n 1


jobs
^^^^

**Usage**: `idmtools container jobs [CONTAINER_ID] [-l LIMIT] [-n NEXT]`

**Arguments**:

- `CONTAINER_ID`: Container ID (optional)
- `-l, --limit`: Max number of simulations to show (default: 10)
- `-n, --next`: Next number of jobs to show (default: 0)

**Description**: List running Experiment/Simulation jobs in Container(s).

**Examples**:

.. code-block:: bash

   $ idmtools container jobs
   $ idmtools container jobs my_container -l 5 -n 1


status
^^^^^^

**Usage**: `idmtools container status ITEM_ID [-c CONTAINER_ID] [-l LIMIT] [--verbose/--no-verbose]`

**Arguments**:

- `ITEM_ID`: Experiment/Simulation ID or Job ID (required)
- `-c, --container_id`: Container ID (optional)
- `-l, --limit`: Max number of simulations to show (default: 10)
- `--verbose/--no-verbose`: Display with working directory or not (default: False)

**Description**: Check the status of an Experiment/Simulation.

**Examples**:

.. code-block:: bash

   $ idmtools container status 6f305619-64b3-ea11-a2c6-c4346bcb1557
   $ idmtools container status 12345
   $ idmtools container status 12345 -c my_container -l 5 --verbose


verify-docker
^^^^^^^^^^^^^

**Usage**: `idmtools container verify-docker`

**Description**: Verify the Docker environment.

**Examples**:

.. code-block:: bash

   $ idmtoolls container verify-docker


get-detail
^^^^^^^^^^

**Usage**: `idmtools container get-detail EXP_ID`

**Arguments**:

- `EXP_ID`: Experiment ID (required)

**Description**: Retrieve Experiment history.

**Examples**:

.. code-block:: bash

   $ idmtools container get-detail 6f305619-64b3-ea11-a2c6-c4346bcb1557


path
^^^^

**Usage**: `idmtools container path ITEM_ID`

**Arguments**:

- `ITEM_ID`: Suite/Experiment/Simulation ID (required)

**Description**: Locate Suite/Experiment/Simulation file directory.

**Examples**:

.. code-block:: bash

   $ idmtools container path 6f305619-64b3-ea11-a2c6-c4346bcb1557


is-running
^^^^^^^^^^

**Usage**: `idmtools container is-running ITEM_ID`

**Arguments**:

- `ITEM_ID`: Experiment/Simulation ID (required)

**Description**: Check if an Experiment/Simulation is running.

**Examples**:

.. code-block:: bash

   $ idmtools container is-running 6f305619-64b3-ea11-a2c6-c4346bcb1557


volume
^^^^^^

**Usage**: `idmtools container volume`

**Description**: Check the history volume.

**Examples**:

.. code-block:: bash

   $ idmtools container volume


clear-history
^^^^^^^^^^^^^

**Usage**: `idmtools container clear-history [CONTAINER_ID]`

**Arguments**:

- `CONTAINER_ID`: Container ID (optional)

**Description**: Clear the job history.

**Examples**:

.. code-block:: bash

   $ idmtools container clear-history
   $ idmtools container clear-history my_container


sync-history
^^^^^^^^^^^^

**Usage**: `idmtools container sync-history`

**Description**: Sync the file system with job history.

**Examples**:

.. code-block:: bash

   $idmtools container sync-history


history-count
^^^^^^^^^^^^^

**Usage**: `idmtools container history-count [CONTAINER_ID]`

**Arguments**:

- `CONTAINER_ID`: Container ID (optional)

**Description**: Get the count of job histories.

**Examples**:

.. code-block:: bash

   $ idmtools container history-count
   $ idmtools container history-count my_container


clear-results
^^^^^^^^^^^^^

**Usage**: `idmtools container clear-results ITEM_ID [-r REMOVE]`

**Arguments**:

- `ITEM_ID`: Experiment/Simulation ID (required)
- `-r, --remove`: Extra files/folders to be removed from simulation (optional, multiple)

**Description**: Clear job results files and folders.

**Examples**:

.. code-block:: bash

   $ idmtools container clear-results 6f305619-64b3-ea11-a2c6-c4346bcb1557
   $ idmtools container clear-results 6f305619-64b3-ea11-a2c6-c4346bcb1557 -r extra_file.txt


inspect
^^^^^^^

**Usage**: `idmtools container inspect CONTAINER_ID`

**Arguments**:

- `CONTAINER_ID`: Container ID (required)

**Description**: Inspect a container.

**Examples**:

.. code-block:: bash

   $ idmtools container inspect my_container


stop-container
^^^^^^^^^^^^^^

**Usage**: `idmtools container stop-container [CONTAINER_ID] [--remove/--no-remove]`

**Arguments**:

- `CONTAINER_ID`: Container ID (optional)
- `--remove/--no-remove`: Remove the container or not (default: False)

**Description**: Stop running container(s).

**Examples**:

.. code-block:: bash

   $ idmtools container stop-container
   $ idmtools container stop-container my_container --remove


remove-container
^^^^^^^^^^^^^^^^

**Usage**: `idmtools container remove-container [CONTAINER_ID]`

**Arguments**:

- `CONTAINER_ID`: Container ID (optional)

**Description**: Remove stopped containers.

**Examples**:

.. code-block:: bash

   $ idmtools container remove-container
   $ idmtools container remove-container my_container


install
^^^^^^^

**Usage**: `idmtools container install PACKAGE [-c CONTAINER_ID] [-i INDEX-URL] [-e EXTRA-INDEX-URL]`

**Arguments**:

- `PACKAGE`: Package to be installed (required)
- `-c, --container_id`: Container ID (optional)
- `-i, --index-url`: Index URL for pip install (optional)
- `-e, --extra-index-url`: Extra index URL for pip install (optional)

**Description**: Pip install a package on a container.

**Examples**:

.. code-block:: bash

   $ idmtools container install requests
   $ idmtools container install requests -c my_container -i https://pypi.org/simple


packages
^^^^^^^^

**Usage**: `idmtools container packages CONTAINER_ID`

**Arguments**:

- `CONTAINER_ID`: Container ID (required)

**Description**: List packages installed on a container.

**Examples**:

.. code-block:: bash

   $ idmtools container packages my_container


ps
^^

**Usage**: `idmtools container ps CONTAINER_ID`

**Arguments**:

- `CONTAINER_ID`: Container ID (required)

**Description**: List running processes in a container.

**Examples**:

.. code-block:: bash

   $ idmtools container ps my_container


list-containers
^^^^^^^^^^^^^^^

**Usage**: `idmtools container list-containers [--all/--no-all]`

**Arguments**:

- `--all/--no-all`: Include stopped containers or not (default: False)

**Description**: List all available containers.

**Examples**:

.. code-block:: bash

   $ idmtools container list-containers
   $ idmtools container list-containers --all


