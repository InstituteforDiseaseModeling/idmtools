import os
import allure
import pytest
import unittest
from idmtools.core import TRUTHY_VALUES
from idmtools.core.platform_factory import Platform
from idmtools_platform_comps.utils.download.download import DownloadWorkItem
from idmtools_test.utils.comps import load_library_dynamically, run_package_dists

TEST_WITH_NEW_CODE = os.environ.get("TEST_WITH_PACKAGES", 'n').lower() in TRUTHY_VALUES


@pytest.mark.comps
@allure.feature("DownloadFilter")
class TestDownloadWorkItem(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        self.platform = Platform("SLURM2")

    @classmethod
    def setUpClass(cls) -> None:
        if TEST_WITH_NEW_CODE:
            run_package_dists()

    def test_comps_dl(self):
        dl_wi = DownloadWorkItem(name=self.case_name, related_experiments=['a299949a-5c29-eb11-a2c2-f0921c167862'], file_patterns=["output.sim"], simulation_prefix_format_str='{simulation.tags["index"]}', verbose=True)
        if TEST_WITH_NEW_CODE:
            dl_wi.add_pre_creation_hook(load_library_dynamically)
        dl_wi.run(wait_on_done=True, platform=self.platform)
        self.assertTrue(dl_wi.succeeded)
