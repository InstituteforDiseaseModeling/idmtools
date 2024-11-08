"""
This script demonstrates:
1. How to run simulation in a Singularity container in a SLURM cluster.
2. How to bind a directory to the singularity container. The reason for binding a directory is that the simulation
    results are written to a directory that is not accessible by default inside the container.

Setup Instructions:
1. First, download the Singularity Image File (SIF) for this example by running the following command in the terminal:
    $ singularity pull ubuntu_d.sif docker://ubuntu:20.04
2. Once downloaded, copy the SIF file ubuntu_d.sif to the /projects/shared_resource/images directory.($ sudo mkdir -p /projects/shared_resource/images)
3. Make sure you have directory /projects/shared_resource/my_tests created ($ sudo mkdir -p /projects/shared_resource/my_tests)
4. Make sure job_directory has permission to write and execute (sudo chmod -R 777 /projects/shared_resource/my_tests)

Script Overview:
- This script defines a SLURM job directory and sets up a command to execute within the Singularity container.
- The command binds the /projects/shared_resource directory and runs a script inside the container (hello.sh).
"""
import sys

from idmtools.core.platform_factory import Platform
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment

# Define the job directory and platform
job_directory = "/projects/shared_resource/my_tests"
# Most of the time, you may need to have partition, account, and modules specified in the platform
platform = Platform('SLURM_LOCAL', job_directory=job_directory)

# Define the task
command = "singularity exec --bind /projects/shared_resource /projects/shared_resource/images/ubuntu_d.sif ./Assets/hello.sh"
task = CommandTask(command=command)
# Add the script to the task
task.common_assets.add_asset("input/hello.sh")

# create experiment from task
experiment = Experiment.from_task(task, name="run_task_in_singularity")
# Run the experiment
experiment.run(platform=platform, wait_until_done=True)
sys.exit(0 if experiment.succeeded else -1)
