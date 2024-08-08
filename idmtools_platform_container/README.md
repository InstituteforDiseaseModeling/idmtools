![Staging: idmtools-platform-container](https://github.com/InstituteforDiseaseModeling/idmtools/workflows/Staging:%20idmtools-platform-container/badge.svg?branch=dev)

# Idmtools Platform Container

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Introduction](#introduction)
- [Setting Up Virtual Environment](#setting-up-virtual-environment)
- [Running a Simple Example with ContainerPlatform](#running-a-simple-example-with-containerplatform)
- [Basic CLI Commands](#basic-cli-commands)
  - [List Running Jobs](#list-running-jobs)
  - [Check Status](#check-status)
  - [Cancel Job](#cancel-job)
  - [View Experiments History](#view-experiments-history)
- [Note](#note)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Introduction

**ContainerPlatform** is a platform designed to facilitate the execution of experiments and simulations within Docker containers. It provides a robust environment with all necessary tools and dependencies installed, allowing for seamless integration and execution of computational tasks.

## Setting Up Virtual Environment

To set up a virtual environment for **ContainerPlatform**, follow these steps:

1. **Install Python**

   Ensure you have Python 3.8+ installed on your system.

2. **Create Virtual Environment**
   
   There are multiple ways to create a virtual environment. Below is an example using `venv`:

    ```bash
    python -m venv container_env
    ```

3. **Activate Virtual Environment**
    - On Windows:
        ```bash
        container_env\Scripts\activate
        ```
    - On Linux:
        ```bash
        source container_env/bin/activate
        ```

4. **Install ContainerPlatform**
    ```bash
    pip install idmtools-platform-container --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple
    ```

5. **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

## Running a Simple Example with ContainerPlatform

To run a simple example using **ContainerPlatform**, please pay attention to the **Note** at the end of the README. Other than that, for a general existing COMPS example, user just needs to change one line code to replace COMPS Platform with Container Platform. Below are the steps:

1. **Initialize Platform**:

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

2. **Create and run an Experiment**

   This step is the same as running an experiment on the COMPS Platform.
   
3. **Use CLI command to check status**
    ```bash
    idmtools container status <experiment id>
    ```

## Basic CLI Commands

**ContainerPlatform** provides several CLI commands to manage and monitor experiments and simulations. Below are some basic commands:

### List Running Jobs

To list running experiment or simulation jobs:
```bash
idmtools container jobs [<container-id>] [-l <limit>] [-n <next>]
```

### Check Status

To check the status of an experiment or simulation:
```bash
idmtools container status <item-id> [-c <container_id>] [-l <limit>] [--verbose/--no-verbose]
```

### Cancel Job

To cancel an experiment or simulation job:
```bash
idmtools container cancel <item-id> [-c <container_id>]
```

### View Experiments History

To view experiments history:
```bash
idmtools container history [<container-id>] [-l <limit>] [-n <next>]
```


## Note

- **WorkItem** is not supported on the Container Platform as it is not needed in most cases since the code already runs on user's local computer.
- **AssetCollection** creation or referencing to an existing AssetCollection are not supported on the Container Platform with current release. If you've used the COMPS Platform, you may have scripts using these objects. You would need to update these scripts without using these objects in order to run them on the Container Platform.
- Run with Singularity is not needed with Container Platform. If you take existing COMPS example and try to run it with Container Platform, you may need to remove the code that setups the singularity image.