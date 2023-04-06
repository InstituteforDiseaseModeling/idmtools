=======================
Run Script As Slurm Job
=======================

This is a temporary workaround solution and user can follow the steps to run a Python script as a Slurm job.

In the future we may develop a utility tool which will run a Python script as a Slurm job automatically.

Steps
....
This guide takes Northwestern University QUEST Slurm system as an example. For general case, users may need to modify the steps based on their own Slurm environment.

Assume user has virtual environment created and activated.

1.Have target script ready, say my_script.py, suppose you have folder structure like::

   script_folder
      my_script.py
      ......

2.within the script folder, create a batch file 'sbatch.sh' (without quote).

   sbatch.sh has content like::

    #!/bin/bash

    #SBATCH --partition=b1139
    #SBATCH --time=10:00:00
    #SBATCH --account=b1139

    #SBATCH --output=stdout.txt
    #SBATCH --error=stderr.txt

    # replace with your script file
    python3 my_script.py

    exit $RESULT


.. note::

    based on user Slurm system, above content may be a little bit different.

3.Run target script as SLURM job
    execute the following command from console (under virtual environment)::

    cd <path to script folder>

    then::

    sbatch sbatch.sh

.. note::

    any output information from my_script.py is stored in file stdout.txt under the current folder. For example, if my_script.py kicks out another Slurm job, then its Slurm id information can be found in file stdout.txt.