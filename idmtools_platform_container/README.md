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

# Introduction

**ContainerPlatform** is a platform designed to facilitate the execution of experiments and simulations within Docker containers. It provides a robust environment with all necessary tools and dependencies installed, allowing for seamless integration and execution of computational tasks.

## Pre-requisites
- Python 3.8/3.9/3.10/3.11/3.12 x64-bit
- OS: 
  - Windows 10 Pro or Enterprise
  - Linux
  - macOS (10.15 Catalina or later) 
- Docker or Docker Desktop(required for the container platform)
  On Windows, please use Docker Desktop 4.0.0 or later
- **Mac user**: Only support Intel based **x86_64** architecture if you want to run emodpy related disease models on **Docker** container platform. Apple based ARM architecture currently is not supported. 

## Installation

- **Install python**

   Ensure you have Python 3.8+ installed on your system.

- Create and activate a virtual environment:
    ```
    python -m venv venv
    source venv/bin/activate  # On macOS/Linux
    venv\Scripts\activate     # On Windows
    ```

- Install all **container** platform related packages
    ```bash
    pip install idmtools[container] --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple
    ```
- Optional: Install all **idmtools** packages
    ```bash
    pip install idmtools[full] --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple
    ```
- To **override** existing idmtools container related packages after installing emodpy, run this command
    ```bash
    pip install idmtools[container] --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple --force-reinstall --no-cache-dir --upgrade
    ``` 
  **Mac user**: You map need to escape the square brackets with a backslash like `\[container\]` or `\[full\]` in above command.

- Extra steps for Windows user:
  - Enable **Developer Mode** on Windows

    If you are running the script on Windows, you need to enable Developer Mode. To enable Developer Mode, go to Settings -> Update & Security -> For developers and select Developer Mode on, or refer to this [guide](https://learn.microsoft.com/en-us/windows/apps/get-started/enable-your-device-for-development).

  - Enable **long file path** for Windows
  
    Due to the file/folder structure design outlined in the section below, if running the script on Windows, be aware of the file path length limitation (less than 255 characters).
  
    To allow longer file paths, you can enable Long Path Support in the Windows Group Policy Editor.
  Refer to this [guide](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/The-Windows-10-default-path-length-limitation-MAX-PATH-is-256-characters.html) for detailed instructions.

## Examples for container platform

### Initialize platform
- This is the example using Container Platform
    ```python 
    from idmtools.core.platform_factory import Platform
    platform = Platform('CONTAINER', job_directory='<user job directory>')
    ```
- To trigger MPI, use ntasks >=2:
    ```python
    from idmtools.core.platform_factory import Platform
    platform = Platform('CONTAINER', job_directory='<user job directory>', ntasks=2)
    ```
- More options for container platform initialization:
    refer to [ContainerPlatform attributes](hhttps://docs.idmod.org/projects/idmtools/en/latest/platforms/container/index.html#containerplatform-attributes)

### Container Examples
  - idmtools examples: https://github.com/InstituteforDiseaseModeling/idmtools/tree/main/examples/platform_container
  - emodpy-malaria examples: https://github.com/EMOD-Hub/emodpy-malaria/tree/main/examples-container


### Check result with CLI commands
    ```bash
    idmtools container status <experiment id>
    ```
### Check result files
    - on host: `<job_directory>/<suite_path>/<experiment_path>/<simulation_path>/`
    - in container: `/home/container-data/<suite_path>/<experiment_path>/<simulation_path>/`


### Folder structure
By default, `idmtools` will generate simulations with the following structure:
`job_directory/suite_name_uuid/experiment_name_uuid/simulation_uuid`
- `job_directory` is the base directory for suite, experiment and simulations.
- `suite_name_uuid` is the name of the suite as prefix plus a suite uuid.
- `experiment_name_uuid` is the name of the experiment plus a experiment uuid.
- `simulation_uuid` is only simulation uuid.

The user can customize the folder structure by setting the following parameters in the `idmtools.ini` file:
- `name_directory = False`: The suite and experiment names will be excluded in the simulation path.
- `sim_name_directory = True`: The simulation name will be included in the simulation path with name_directory is True.



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
