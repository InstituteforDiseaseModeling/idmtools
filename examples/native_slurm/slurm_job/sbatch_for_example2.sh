#!/bin/bash

#SBATCH --partition=b1139
#SBATCH --time=10:00:00
#SBATCH --account=b1139

#SBATCH --output=stdout.txt
#SBATCH --error=stderr.txt

# replace with your script file
python3 example2.py

exit $RESULT