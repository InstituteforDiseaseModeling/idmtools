![Staging: idmtools-platform-slurm](https://github.com/InstituteforDiseaseModeling/idmtools/workflows/Staging:%20idmtools-platform-slurm/badge.svg?branch=dev)

# idmtools-platform-slurm

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Development Tips](#development-tips)
- [Manually run a script as a Slurm job](#manually-run-a-script-as-a-slurm-job)
- [Use SlurmJob to run a script as a Slurm job](#use-slurmjob-to-run-a-script-as-a-slurm-job)
- [script = 'example_path/python_sim_slurm.py'   &#035; example](#script--example_pathpython_sim_slurmpy----example)
- [With SlurmPlaform to run a script as a Slurm job](#with-slurmplaform-to-run-a-script-as-a-slurm-job)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->


# Development Tips

There is a Makefile file available for most common development tasks. Here is a list of commands

```bash
clean       -   Clean up temproary files
lint        -   Lint package and tests
test        -   Run All tests
coverage    -   Run tests and generate coverage report that is shown in browser
```

On Windows, you can use `pymake` instead of `make`


# Manually run a script as a Slurm job

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

then

   sbatch sbatch.sh

Note: any output information from my_script.py is stored in file stdout.txt under the current folder. For example, if my_script.py kicks out another Slurm job, then its Slurm id information can be found in file stdout.txt.


# Use SlurmJob to run a script as a Slurm job

The example can be simple as the following:

--script.py--

from idmtools.core.platform_factory import Platform
from idmtools_platform_slurm.utils.slurm_job.slurm_job import SlurmJob

script = '<user script path>'
# script = 'example_path/python_sim_slurm.py'   # example
platform = Platform('SLURM_LOCAL', job_directory='<job_directory>')
sj = SlurmJob(script_path=script, platform=platform)
sj.run()


# With SlurmPlaform to run a script as a Slurm job

We have SlurmJob integrated into SlurmPlatform and any Python script can run as a Slurm job simply doing:

--script.py--

from idmtools.core.platform_factory import Platform
platform = Platform('SLURM_LOCAL', job_directory='<job_directory>', run_on_slurm=True)
print('below content will run on Slurm as a job.')
......

