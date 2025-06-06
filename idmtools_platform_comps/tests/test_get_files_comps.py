import unittest
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform


class TestCOMPSGetFiles(unittest.TestCase):
    def setUp(self):
        self.platform = Platform('SlurmStage')
        self.case_name = f"output/{self._testMethodName}"

    def test_get_files_simulation(self):
        sim_id = "24061284-d33d-f011-9310-f0921c167864"
        simulation = self.platform.get_item(sim_id, ItemType.SIMULATION, raw=False)
        files = ["output/result.json", "StdOut.txt", "Assets/model1.py"]
        ret_files = self.platform.get_files(simulation, files=files, output=self.case_name)
        self.assertEqual(len(ret_files), 3)
        self._verify_files(ret_files, files)

    def test_get_files_simulation_comps(self):
        sim_id = "24061284-d33d-f011-9310-f0921c167864"
        simulation = self.platform.get_item(sim_id, ItemType.SIMULATION, raw=True)
        files = ["output/result.json", "StdOut.txt", "Assets/model1.py"]
        ret_files = self.platform.get_files(simulation, files=files, output=self.case_name)
        self.assertEqual(len(ret_files), 3)
        self._verify_files(ret_files, files)

    def test_get_files_by_id_simulations(self):
        files = ["output/result.json", "StdOut.txt", "Assets/model1.py"]
        ret_files = self.platform.get_files_by_id("24061284-d33d-f011-9310-f0921c167864",
                                                  item_type=ItemType.SIMULATION, files=files, output=self.case_name)
        self.assertEqual(len(ret_files), 3)
        self._verify_files(ret_files, files)

    def test_get_files_work_item(self):
        workitem_id = "5481358e-4b0e-f011-930e-f0921c167864"
        workitem = self.platform.get_item(workitem_id, ItemType.WORKFLOW_ITEM, raw=False)
        #files = ["WorkOrder.json", "Assets/Singularity.def"]
        files = ["WorkOrder.json", "stdout.txt"]
        ret_files = self.platform.get_files(workitem, files=files, output=self.case_name)
        self.assertEqual(len(ret_files), 2)
        self._verify_files(ret_files, files)

    def test_get_files_work_item_comps(self):
        workitem_id = "5481358e-4b0e-f011-930e-f0921c167864"
        workitem = self.platform.get_item(workitem_id, ItemType.WORKFLOW_ITEM, raw=True)
        files = ["WorkOrder.json", "stdout.txt"]
        ret_files = self.platform.get_files(workitem, files=files, output=self.case_name)
        self.assertEqual(len(ret_files), 2)
        self._verify_files(ret_files, files)

    def test_get_files_by_id_work_item(self):
        files = ["WorkOrder.json", "stdout.txt"]
        ret_files = self.platform.get_files_by_id("5481358e-4b0e-f011-930e-f0921c167864",
                                                  item_type=ItemType.WORKFLOW_ITEM, files=files, output=self.case_name)
        self.assertEqual(len(ret_files), 2)
        self._verify_files(ret_files, files)

    def test_get_files_asset_collection(self):
        ac_id = "475445f2-9359-ef11-9306-f0921c167864"
        ac = self.platform.get_item(ac_id, ItemType.ASSETCOLLECTION, raw=False)
        files = ["model.py", "MyExternalLibrary/functions.py"]
        ret_files = self.platform.get_files(ac, files=files, output=self.case_name)
        self.assertEqual(len(ret_files), 2)
        self._verify_files(ret_files, files)

    def test_get_files_asset_collection_comps(self):
        ac_id = "475445f2-9359-ef11-9306-f0921c167864"
        ac = self.platform.get_item(ac_id, ItemType.ASSETCOLLECTION, raw=True)
        files = ["model.py", "MyExternalLibrary/functions.py"]
        ret_files = self.platform.get_files(ac, files=files, output=self.case_name)
        self.assertEqual(len(ret_files), 2)
        self._verify_files(ret_files, files)

    def test_get_files_by_id_asset_collection(self):
        files = ["model.py", "MyExternalLibrary/functions.py"]
        ret_files = self.platform.get_files_by_id("475445f2-9359-ef11-9306-f0921c167864",
                                                  item_type=ItemType.ASSETCOLLECTION, files=files, output=self.case_name)
        self.assertEqual(len(ret_files), 2)
        self._verify_files(ret_files, files)

    def test_get_files_experiment_comps(self):
        exp_id = "1e061284-d33d-f011-9310-f0921c167864"
        experiment = self.platform.get_item(exp_id, ItemType.EXPERIMENT, raw=True)
        simulations = self.platform._get_children_for_platform_item(experiment)
        files = ["output/result.json", "StdOut.txt"]
        ret_files = self.platform.get_files(experiment, files=files, output=self.case_name)
        for sim in simulations:
            convert_file_path = []
            for key, value in ret_files[str(sim.id)].items():
                convert_file_path.append(key.replace("\\", "/"))
                self.assertIsNotNone(value)
                self.assertTrue(len(value) > 0)
            assert set(convert_file_path) == set(files)

    def test_get_files_experiment(self):
        exp_id = "1e061284-d33d-f011-9310-f0921c167864"
        experiment = self.platform.get_item(exp_id, ItemType.EXPERIMENT, raw=False)
        files = ["output/result.json", "StdOut.txt"]
        ret_files = self.platform.get_files(experiment, files=files, output=self.case_name)
        for sim in experiment.simulations:
            convert_file_path = []
            for key, value in ret_files[sim.id].items():
                convert_file_path.append(key.replace("\\", "/"))
                self.assertIsNotNone(value)
                self.assertTrue(len(value) > 0)
            assert set(convert_file_path) == set(files)

    def test_get_files_suite_comps(self):
        suite_id = "3523bca7-5c42-f011-9310-f0921c167864"
        suite = self.platform.get_item(suite_id, ItemType.SUITE, raw=True)
        files = ["output/output.json", "config.json"]
        ret_files = self.platform.get_files(suite, files=files, output=self.case_name)
        experiments = self.platform._get_children_for_platform_item(suite)
        for experiment in experiments:
            simulations = self.platform._get_children_for_platform_item(experiment)
            ret = ret_files[str(experiment.id)]
            for sim in simulations:
                convert_file_path = []
                for key, value in ret[str(sim.id)].items():
                    convert_file_path.append(key.replace("\\", "/"))
                    self.assertIsNotNone(value)
                    self.assertTrue(len(value) > 0)
                assert set(convert_file_path) == set(files)

    def test_get_files_suite(self):
        suite_id = "3523bca7-5c42-f011-9310-f0921c167864"
        suite = self.platform.get_item(suite_id, ItemType.SUITE, raw=False)
        files = ["output/output.json", "config.json"]
        ret_files = self.platform.get_files(suite, files=files, output=self.case_name)
        experiments = suite.experiments
        for experiment in experiments:
            simulations = experiment.simulations
            ret = ret_files[str(experiment.id)]
            for sim in simulations:
                convert_file_path = []
                for key, value in ret[str(sim.id)].items():
                    convert_file_path.append(key.replace("\\", "/"))
                    self.assertIsNotNone(value)
                    self.assertTrue(len(value) > 0)
                assert set(convert_file_path) == set(files)

    def _verify_files(self, actual_files, expected_files):
        convert_file_path = []
        for key, value in actual_files.items():
            convert_file_path.append(key.replace("\\", "/"))
            self.assertIsNotNone(value)
            self.assertTrue(len(value) > 0)
        assert set(convert_file_path) == set(expected_files)
