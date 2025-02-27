![Staging: idmtools-platform-container](https://github.com/InstituteforDiseaseModeling/idmtools/workflows/Staging:%20idmtools-platform-container/badge.svg?branch=dev)

# Idmtools platform container

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Introduction](#introduction)
- [Pre-requisites](#pre-requisites)
- [Setting up virtual environment](#setting-up-virtual-environment)
- [Running a simple example with ContainerPlatform](#running-a-simple-example-with-containerplatform)
- [Basic CLI commands](#basic-cli-commands)
  - [List running jobs](#list-running-jobs)
  - [Check status](#check-status)
  - [Cancel job](#cancel-job)
  - [View Experiments history](#view-experiments-history)
- [Note](#note)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Introduction

**ContainerPlatform** is a platform designed to facilitate the execution of experiments and simulations within Docker containers. It provides a robust environment with all necessary tools and dependencies installed, allowing for seamless integration and execution of computational tasks.

## Pre-requisites
- Python 3.8/3.9/3.10/3.11/3.12 x64-bit
- Windows 10 Pro or Enterprise, or a Linux operating system
- Docker(required for the container platform)
  On Windows, please use Docker Desktop 4.0.0 or later

## Setting up virtual environment

To set up a virtual environment for **ContainerPlatform**, follow these steps:

1. **Install python**

   Ensure you have Python 3.8+ installed on your system.

2. **Create virtual environment**
   
   There are multiple ways to create a virtual environment. Below is an example using `venv`:

    ```bash
    python -m venv container_env
    ```

3. **Activate virtual environment**
    - On Windows:
        ```bash
        container_env\Scripts\activate
        ```
    - On Linux:
        ```bash
        source container_env/bin/activate
        ```

4. **Install idmtools-platform-container**
    ```bash
    pip install idmtools-platform-container --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple
    ```

5. **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```
   
6. **Optional install all container platform related packages (skip step #4 and #5)**
    ```bash
    pip install idmtools[container] --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple
    ```
7. **Enable Developer Mode on Windows**

    If you are running the script on Windows, you need to enable Developer Mode. To enable Developer Mode, go to `Settings -> Update & Security -> For developers` and select `Developer Mode` on.


8. **Enable long file path on Windows**

    If running the script on Windows, be aware of the file path length limitation (less than 255 characters).
    If you really need to run the script with long file paths, you can set the Enable Long Path Support in Windows Group Policy Editor. refer to https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/The-Windows-10-default-path-length-limitation-MAX-PATH-is-256-characters.html.

## Running a simple example with ContainerPlatform

To run a simple example using **ContainerPlatform**, please pay attention to the **Note** at the end of the README. Other than that, for a general existing COMPS example, user just needs to change one line code to replace COMPS Platform with Container Platform. Below are the steps:

1. **Initialize platform**:

    This is an example using COMPS Platform
    ```python
   
    from idmtools.core.platform_factory import Platform
    platform = Platform('CALCULON')
   
    ```

    This is the example using Container Platform
    ```python
   
    from idmtools.core.platform_factory import Platform
    platform = Platform('CONTAINER', job_directory='<user job directory>')
   
    ```
   
2. **Folder structure**:

    By default, `idmtools` will generate simulations with the following structure:
    `job_directory/suite_name_uuid/experiment_name_uuid/simulation_uuid`

    - `job_directory` is the base directory for suite, experiment and simulations.
    - `suite_name_uuid` is the name of the suite as prefix plus a suite uuid.
    - `experiment_name_uuid` is the name of the experiment plus a experiment uuid.
    - `simulation_uuid` is only simulation uuid.

    The user can customize the folder structure by setting the following parameters in the `idmtools.ini` file:
    - `name_directory = False`: The suite and experiment names will be excluded in the simulation path.
    - `sim_name_directory = True`: The simulation name will be included in the simulation path with name_directory is True.

    **Note**: If running the script on Windows, be aware of the file path length limitation (less than 255 characters).
    If you really need to run the script with long file paths, you can set the Enable Long Path Support in Windows Group Policy Editor. refer to https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/The-Windows-10-default-path-length-limitation-MAX-PATH-is-256-characters.html.
     

3. **Create and run an Experiment**

   This step is the same as running an experiment on the COMPS Platform.
   
4. **Use CLI command to check status**
    ```bash
    idmtools container status <experiment id>
    ```
5. **Check simulation results in files**

    Once the experiment is completed, the results can be viewed in the output directory. The output directory is like
    `<job_directory>/<suite_path>/<experiment_path>/<simulation_path>/`.

    The same results can be viewed in the container as well. The output directory in the container is like
    `/home/container-data/<suite_path>/<experiment_path>/<simulation_path>/`.

## Basic CLI commands

**ContainerPlatform** provides several CLI commands to manage and monitor experiments and simulations. Below are some basic commands:

### List running jobs

To list running experiment or simulation jobs:
```bash
idmtools container jobs [<container-id>] [-l <limit>] [-n <next>]
```

### Check status

To check the status of an experiment or simulation:
```bash
idmtools container status <item-id> [-c <container_id>] [-l <limit>] [--verbose/--no-verbose]
```

### Cancel job

To cancel an experiment or simulation job:
```bash
idmtools container cancel <item-id> [-c <container_id>]
```

### View Experiments history

To view experiments history:
```bash
idmtools container history [<container-id>] [-l <limit>] [-n <next>]
```


## Note

- **WorkItem** is not supported on the Container Platform as it is not needed in most cases since the code already runs on user's local computer.
- **AssetCollection** creation or referencing to an existing AssetCollection are not supported on the Container Platform with current release. If you've used the COMPS Platform, you may have scripts using these objects. You would need to update these scripts without using these objects in order to run them on the Container Platform.
- Run with Singularity is not needed with Container Platform. If you take existing COMPS example and try to run it with Container Platform, you may need to remove the code that setups the singularity image.