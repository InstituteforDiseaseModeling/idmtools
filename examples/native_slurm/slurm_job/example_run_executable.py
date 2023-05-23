"""
 This example shows how to run executable with script on slurm job with SlurmJob class
 The example runs 'bash batch.sh p1 p2' behind the scenes in slurm computation node while 'bash' is executable,
 'batch.sh' is script for SlurmJob. We also pass p1, p2 parameters to batch script as commandline parameters

 To run the example, there are 2 options:
    - python example_run_executable.py Joe Fisher (Note, you can give any two strings to replace 'Joe' and 'Fisher')
    - python example_run_executable.py (Note, uses default values for p1 and p2 in this script)
 To see result for the example, open stdout.txt file

 Note, actual experiment is created by nested slurm job which you can find job id in stdout.out of current running dir
"""

import os

from idmtools.core.platform_factory import Platform
from idmtools_platform_slurm.utils.slurm_job.slurm_job import SlurmJob

import argparse

parser = argparse.ArgumentParser(description='enter parameters')
parser.add_argument('p1', nargs='?', default='Joe', help='Any string')
parser.add_argument('p2', nargs='?', default='Chris', help='Any string')
args = parser.parse_args()

current_dir = os.path.dirname(__file__)
script_path = os.path.join(current_dir, 'batch.sh')
platform = Platform('SLURM_LOCAL', job_directory="DEST", partition='b1139', time='10:00:00', account='b1139')
sj = SlurmJob(platform=platform, executable='bash', script_path=script_path, script_params=[args.p1, args.p2])
sj.run()

