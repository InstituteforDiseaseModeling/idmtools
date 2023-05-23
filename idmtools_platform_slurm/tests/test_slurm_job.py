import os
import unittest

import pytest
from idmtools.core.platform_factory import Platform
from idmtools_platform_slurm.utils.slurm_job.slurm_job import SlurmJob
from idmtools_test.utils.decorators import linux_only


@pytest.mark.serial
@linux_only
class SlurmJobDryrRunTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.current_dir = os.path.dirname(__file__)
        script_path = os.path.join(cls.current_dir, 'input', 'script.py')
        platform = Platform('SLURM_LOCAL', job_directory=os.path.join(cls.current_dir, "DEST"))
        script_params = ['20', '1', '2', '3']
        sj = SlurmJob(script_path=script_path, platform=platform, script_params=script_params)
        sj.run(dry_run=True)

    def setup(self):
        try:
            # Delete existing sbatch.sh file
            os.remove(os.path.join(self.current_dir, 'input', 'sbatch.sh'))
            print("File deleted successfully.")
        except OSError as e:
            pass

    def test_sbatch_created(self):
        self.assertTrue(os.path.exists(os.path.join(self.current_dir, 'input', 'sbatch.sh')))
        with open(os.path.join(self.current_dir, 'input', 'sbatch.sh'), 'r') as fpr:
            contents = fpr.read()
        self.assertIn("python3 script.py 20 1 2 3", contents)
