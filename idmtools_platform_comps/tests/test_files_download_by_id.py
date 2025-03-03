import os
import tempfile
import unittest
from pathlib import Path

from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform


class TestPlatformFileDownload(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up resources for all tests in this class."""
        cls.platform = Platform("SlurmStage")
        cls.ac_id = "3d2b5ab3-27f6-ef11-930d-f0921c167864"

    def setUp(self):
        """Set up resources for each test."""
        self.output_path = tempfile.mkdtemp()

    def test_assetcollection_files_download(self):
        """
        Test downloading files from the platform.
        For this testcase, we will download all files from out_filenames list except the last one "b.txt" because it does not exist in assetcollection.
        """
        out_filenames = ["a_test.txt", "data/a_test", "data/a_test.txt", "B.txt", "b.txt", "Assets/a_test.txt"]
        d = self.platform.get_files_by_id(
            self.ac_id,
            ItemType.ASSETCOLLECTION,
            out_filenames,
            self.output_path
        )
        # Expect only first 4 files to be downloaded
        expected_files = [str(Path(os.path.join(self.output_path, self.ac_id, f))) for f in out_filenames[:4]]

        # Get all files in the output_path directory
        downloaded_files = []
        # Walk through the directory and its subdirectories
        for root, dirs, files in os.walk(os.path.join(self.output_path, self.ac_id)):
            for file in files:
                # Construct the full file path
                full_path = os.path.join(root, file)
                downloaded_files.append(full_path)

        self.assertTrue(all([f in downloaded_files for f in expected_files]))
        self.assertFalse([s for s in downloaded_files if out_filenames[4] in s])  # b.txt is not in the downloaded_files list
        self.assertFalse([s for s in downloaded_files if out_filenames[5] in s])  # Assets/a_test.txt is not in the downloaded_files list

    def test_simulation_files_download(self):
        out_filenames = ['stdout.txt', 'stderr.txt', 'Assets/a_test.txt']
        sim_id = "084eb953-3af6-ef11-930d-f0921c167864"
        d = self.platform.get_files_by_id(
            sim_id,
            ItemType.SIMULATION,
            out_filenames,
            self.output_path
        )
        expected_files = [str(Path(os.path.join(self.output_path, sim_id, f))) for f in out_filenames]
        self.assertTrue(all([os.path.exists(f) for f in expected_files]))
        self.assertFalse(os.path.exists(os.path.join(self.output_path, sim_id, "random.txt")))

    def test_simulation_file_download_no_exist_file(self):
        out_filenames = ['random.txt']
        sim_id = "084eb953-3af6-ef11-930d-f0921c167864"
        try:
            d = self.platform.get_files_by_id(
                sim_id,
                ItemType.SIMULATION,
                out_filenames,
                self.output_path
            )
        except Exception as e:
            self.assertEqual(str(e), f"Couldn't find file for path 'random.txt'")

    def test_workitem_files_download(self):
        out_filenames = ['stdout.txt', 'stderr.txt', 'WorkOrder.json']
        wi_id = "f6030963-c1ce-ef11-930b-f0921c167864"
        d = self.platform.get_files_by_id(
            wi_id,
            ItemType.WORKFLOW_ITEM,
            out_filenames,
            self.output_path
        )
        expected_files = [str(Path(os.path.join(self.output_path, wi_id, f))) for f in out_filenames]
        self.assertTrue(all([os.path.exists(f) for f in expected_files]))

    def test_workitem_files_download_no_exist_file(self):
        out_filenames = ['random.txt']
        wi_id = "f6030963-c1ce-ef11-930b-f0921c167864"
        try:
            d = self.platform.get_files_by_id(
                wi_id,
                ItemType.WORKFLOW_ITEM,
                out_filenames,
                self.output_path
            )
        except Exception as e:
            self.assertEqual(str(e), f"Couldn't find file for path 'random.txt'")

    def test_experiment_file_download_not_support(self):
        out_filenames = ['anything']
        exp_id = "074eb953-3af6-ef11-930d-f0921c167864"
        try:
            d = self.platform.get_files_by_id(
                exp_id,
                ItemType.EXPERIMENT,
                out_filenames,
                self.output_path
            )
        except Exception as e:
            self.assertEqual(e.args[0], "Item Type: <class 'idmtools.entities.experiment.Experiment'> is not supported!")
