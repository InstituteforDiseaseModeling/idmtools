import os

import pytest

from idmtools import IdmConfigParser
from idmtools.core.platform_factory import Platform
from idmtools_platform_slurm.slurm_operations.slurm_constants import SlurmOperationalMode
from idmtools_test.utils.decorators import linux_only
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence


@pytest.mark.serial
@linux_only
class TestSlurmBridge(ITestWithPersistence):
    def test_init(self):
        IdmConfigParser.clear_instance()
        IdmConfigParser(file_name="idmtools_bridged.ini")
        platform = Platform('BRIDGE', job_directory=".")
        self.assertEqual(platform.mode, SlurmOperationalMode.BRIDGED)
        self.assertEqual(platform.bridged_jobs_directory,
                         os.path.join(os.path.expanduser('~'), ".idmtools", "singularity-bridge"))
        self.assertEqual(platform.bridged_results_directory,
                         os.path.join(os.path.expanduser('~'), ".idmtools", "singularity-bridge", "results"))

    def test_bridge_alias(self):
        platform = Platform('SLURM_BRIDGED', job_directory=".")
        self.assertEqual(platform.mode, SlurmOperationalMode.BRIDGED)
        self.assertEqual(platform.bridged_jobs_directory,
                         os.path.join(os.path.expanduser('~'), ".idmtools", "singularity-bridge"))
        self.assertEqual(platform.bridged_results_directory,
                         os.path.join(os.path.expanduser('~'), ".idmtools", "singularity-bridge", "results"))
