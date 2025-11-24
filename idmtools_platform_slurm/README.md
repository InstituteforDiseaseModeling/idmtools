![Staging: idmtools-platform-slurm](https://github.com/InstituteforDiseaseModeling/idmtools/workflows/Staging:%20idmtools-platform-slurm/badge.svg?branch=dev)

# idmtools-platform-slurm

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Introduction](#introduction)
- [Setting Up Virtual Environment](#setting-up-virtual-environment)
- [Development Tips](#development-tips)
- [Manually run a script as a Slurm job](#manually-run-a-script-as-a-slurm-job)
- [Use SlurmJob to run a script as a Slurm job](#use-slurmjob-to-run-a-script-as-a-slurm-job)
- [With SlurmPlatform to run a script as a Slurm job](#with-slurmplatform-to-run-a-script-as-a-slurm-job)
- [Folder structure:](#folder-structure)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Introduction

**SlurmPlatform** is a platform designed to facilitate the execution of experiments and simulations in slurm cluster. 

## Setting Up Virtual Environment

To set up a virtual environment for **SlurmPlatform**, follow these steps:

1. **Install Python**

   Ensure you have Python 3.8+ installed on your system.

2. **Create Virtual Environment**
   
   There are multiple ways to create a virtual environment. Below is an example using `venv`:

    ```bash
    python -m venv slurm_env
    ```

3. **Activate Virtual Environment**
    - On Windows:
        ```bash
        slurm_env\Scripts\activate
        ```
    - On Linux:
        ```bash
        source slurm_env/bin/activate
        ```

4. **Install SlurmPlatform**
    ```bash
    pip install idmtools-platform-slurm --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple
    ```

5. **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```
6. **Optional(No need step #4 and #5), Install all slurm platform related packages**
    ```bash
    pip install idmtools[slurm] --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple
    ```

## Development Tips

There is a Makefile file available for most common development tasks. Here is a list of commands

```bash
clean       -   Clean up temproary files
lint        -   Lint package and tests
test        -   Run All tests
coverage    -   Run tests and generate coverage report that is shown in browser
```

On Windows, you can use `pymake` instead of `make`


## Manually run a script as a Slurm job

Preparation

(1).Have target script ready, say my_script.py, suppose you have folder structure like::

```bash
script_folder
    my_script.py
    ......
```

(2). Created a virtual environment and activated it.

Steps

1. within the target script folder, create a batch file 'sbatch.sh' (without quote) with content:

```bash
#!/bin/bash

#SBATCH --partition=b1139
#SBATCH --time=10:00:00
#SBATCH --account=b1139

#SBATCH --output=stdout.txt
#SBATCH --error=stderr.txt

# replace with your script file
python3 my_script.py
    
exit $RESULT
```

Note: the content here is based on Northwestern University QUEST Slurm system. For general case, above content (required #SBATCH parameters) may be a little bit different.

2. run your target script as SLURM job
   execute the following commands from console (under virtual environment):

   cd path_to_script_folder

   `sbatch sbatch.sh`

Note: any output information from my_script.py is stored in file stdout.txt under the current folder. For example, if my_script.py kicks out another Slurm job, then its Slurm id information can be found in file stdout.txt.


## Use SlurmJob to run a script as a Slurm job

The example can be simple as the following:

--script.py--

```python

   from idmtools.core.platform_factory import Platform
   from idmtools_platform_slurm.utils.slurm_job.slurm_job import SlurmJob

   script = '<user script path>'
   # script = 'example_path/python_sim_slurm.py'   # example
   platform = Platform('SLURM_LOCAL', job_directory='<job_directory>')
   sj = SlurmJob(script_path=script, platform=platform)
   sj.run()
```

## With SlurmPlatform to run a script as a Slurm job

We have SlurmJob integrated into SlurmPlatform and any Python script can run as a Slurm job simply doing:

--script.py--
```python

   from idmtools.entities.command_task import CommandTask
   from idmtools.entities.experiment import Experiment
   from idmtools.core.platform_factory import Platform
   
   platform = Platform('SLURM_LOCAL', job_directory='<job_directory>')
   # Define task
   command = "echo 'Hello, World!'"
   task = CommandTask(command=command)
   # Run an experiment
   experiment = Experiment.from_task(task, name="example")
   experiment.run(platform=platform)
```

## Folder structure:
[See Folder Structure](../idmtools_platform_container/README.md#folder-structure)