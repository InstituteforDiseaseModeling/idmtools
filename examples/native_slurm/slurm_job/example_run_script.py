"""
 This example shows how to run 'script.py' on slurm job with SlurmJob class
 Originally, script.py runs job on headnode then run experiment/simulation on slurm job
 With SlurmJob as a wrapper, we can directly run script.py on slurm job.
 Note, actual experiment is created by nested slurm job which you can find job id in stdout.out of current running dir
"""

import os

from idmtools.core.platform_factory import Platform
from idmtools_platform_slurm.utils.slurm_job.slurm_job import SlurmJob

current_dir = os.path.dirname(__file__)
script_path = os.path.join(current_dir, 'script.py')
platform = Platform('SLURM_LOCAL', job_directory="DEST", partition='b1139', time='10:00:00', account='b1139')
sj = SlurmJob(script_path=script_path, platform=platform)
sj.run()
