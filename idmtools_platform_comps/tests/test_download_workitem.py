import os
import shutil
import tempfile
from glob import glob
from pathlib import PurePath
import allure
import pytest
import unittest
from idmtools.core.platform_factory import Platform
from idmtools_platform_comps.utils.download.download import DownloadWorkItem, CompressType
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.test_precreate_hooks import TEST_WITH_NEW_CODE
from idmtools_test.utils.comps import run_package_dists
from idmtools_test.utils.decorators import linux_only, windows_only
from idmtools_test.utils.utils import get_case_name


@pytest.mark.comps
@allure.feature("DownloadFilter")
class TestDownloadWorkItem(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.case_name = get_case_name(os.path.basename(__file__) + "--" + self._testMethodName)
        self.platform = Platform("SlurmStage")

    @classmethod
    def setUpClass(cls) -> None:
        if TEST_WITH_NEW_CODE:
            run_package_dists()

    @linux_only
    def test_default_compress_type_linux(self):
        di = DownloadWorkItem()
        self.assertEqual(di.compress_type, CompressType.lzma)

    @windows_only
    def test_default_compress_windows(self):
        di = DownloadWorkItem()
        self.assertEqual(di.compress_type, CompressType.lzma)

    @windows_only
    def test_default_compress_windows_no_delete(self):
        di = DownloadWorkItem(delete_after_download=False)
        self.assertEqual(di.compress_type, CompressType.deflate)

        di = DownloadWorkItem(extract_after_download=False)
        self.assertEqual(di.compress_type, CompressType.deflate)

    def test_comps_download(self):
        try:
            dirpath = tempfile.mkdtemp()
            dl_wi = DownloadWorkItem(name=self.case_name,
                                     related_experiments=['73ba8f3b-8848-ee11-92fb-f0921c167864'], file_patterns=["output/*.csv"],
                                     simulation_prefix_format_str='{simulation.tags["a"]}_{simulation.tags["b"]}', verbose=True, output_path=dirpath, delete_after_download=False, compress_type=CompressType.deflate
                                     )
            dl_wi.run(wait_until_done=True, platform=self.platform)
            self.assertTrue(dl_wi.succeeded)
            files_downloaded = list(glob(os.path.join(dirpath, "**"), recursive=True))
            self.assertEqual(len([x for x in files_downloaded if os.path.isfile(x) and x.endswith(".csv")]), 27)
            self.assertEqual(len([x for x in files_downloaded if os.path.isdir(x) and "output" in x]), 9)
            self.assertTrue(os.path.exists(os.path.join(dirpath, "output.zip")))
        finally:
            shutil.rmtree(dirpath)

    def test_inputs_as_id_files(self):
        id_file = PurePath(COMMON_INPUT_PATH).joinpath('id_files/slurm.example_python_experiment.id')
        try:
            dirpath = tempfile.mkdtemp()
            dl_wi = DownloadWorkItem(name=self.case_name,
                                     related_experiments=[id_file], file_patterns=["output/*.csv"],
                                     simulation_prefix_format_str='{simulation.tags["a"]}_{simulation.tags["b"]}', verbose=True, output_path=dirpath,
                                     )
            dl_wi.run(wait_until_done=True, platform=self.platform)
            self.assertTrue(dl_wi.succeeded)
            files_downloaded = list(glob(os.path.join(dirpath, "**"), recursive=True))
            self.assertEqual(len([x for x in files_downloaded if os.path.isfile(x)]), 27)
            self.assertEqual(len([x for x in files_downloaded if os.path.isdir(x) and "output" in x]), 9)
            self.assertTrue(not os.path.exists(os.path.join(dirpath, "output.zip")))
        finally:
            shutil.rmtree(dirpath)
