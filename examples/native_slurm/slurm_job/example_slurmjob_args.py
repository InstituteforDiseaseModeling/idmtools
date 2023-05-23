"""
Example to demo how to use slurmjob with commandline args
To run: "python example_slurmjob_args.py 20 1 2 3 4" from command line
To find slurmjob id for real experiment/simulations, open stdout.txt for details
"""
import os
import sys

from idmtools.core.platform_factory import Platform
from idmtools_platform_slurm.utils.slurm_job.slurm_job import SlurmJob

current_dir = os.path.dirname(__file__)
script_path = os.path.join(current_dir, 'script_with_args.py')
platform = Platform('SLURM_LOCAL', job_directory=os.path.join(current_dir, "DEST"), partition='b1139', time='10:00:00',
                        account='b1139')

# sys,argv[1:] should be like  ['20', '1', '2', '3', '4'] which from commandline and will be used by script_with_args.py for sweeping
sj = SlurmJob(script_path=script_path, platform=platform, script_params=sys.argv[1:])
sj.run()

