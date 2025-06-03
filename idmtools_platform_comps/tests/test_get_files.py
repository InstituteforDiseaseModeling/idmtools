import unittest
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform


class TestGetFiles(unittest.TestCase):
    def setUp(self):
        self.platform = Platform('SlurmStage')
        self.case_name = self._testMethodName

    def test_getfiles_simulation(self):
        sim_id = "24061284-d33d-f011-9310-f0921c167864"
        simulation = self.platform.get_item(sim_id, ItemType.SIMULATION, raw=False)
        files = ["output/result.json", "StdOut.txt"]
        ret_files = self.platform.get_files(simulation, files=files, output=self.case_name)
        self.assertEqual(len(ret_files), 2)
        self._verify_files(ret_files, files)

    def test_getfiles_comps_comps_simulation(self):
        sim_id = "24061284-d33d-f011-9310-f0921c167864"
        simulation = self.platform.get_item(sim_id, ItemType.SIMULATION, raw=True)
        files = ["output/result.json", "StdOut.txt"]
        ret_files = self.platform.get_files(simulation, files=files, output=self.case_name)
        self.assertEqual(len(ret_files), 2)
        self._verify_files(ret_files, files)

    def test_get_files_by_id_simulations(self):
        files = ["output/result.json", "StdOut.txt"]
        ret_files = self.platform.get_files_by_id("24061284-d33d-f011-9310-f0921c167864",
                                                  item_type=ItemType.SIMULATION, files=files, output=self.case_name)
        self.assertEqual(len(ret_files), 2)
        self._verify_files(ret_files, files)

    def test_getfiles_workitem(self):
        workitem_id = "5481358e-4b0e-f011-930e-f0921c167864"
        workitem = self.platform.get_item(workitem_id, ItemType.WORKFLOW_ITEM, raw=False)
        #files = ["WorkOrder.json", "Assets/Singularity.def"]
        files = ["WorkOrder.json", "stdout.txt"]
        ret_files = self.platform.get_files(workitem, files=files, output=self.case_name)
        self.assertEqual(len(ret_files), 2)
        self._verify_files(ret_files, files)

    def test_getfiles_comps_workitem(self):
        workitem_id = "5481358e-4b0e-f011-930e-f0921c167864"
        workitem = self.platform.get_item(workitem_id, ItemType.WORKFLOW_ITEM, raw=True)
        files = ["WorkOrder.json", "stdout.txt"]
        ret_files = self.platform.get_files(workitem, files=files, output=self.case_name)
        self.assertEqual(len(ret_files), 2)
        self._verify_files(ret_files, files)

    def test_get_files_by_id_workitem(self):
        files = ["WorkOrder.json", "stdout.txt"]
        ret_files = self.platform.get_files_by_id("5481358e-4b0e-f011-930e-f0921c167864",
                                                  item_type=ItemType.WORKFLOW_ITEM, files=files, output=self.case_name)
        self.assertEqual(len(ret_files), 2)
        self._verify_files(ret_files, files)

    def test_getfiles_accesscollection(self):
        ac_id = "475445f2-9359-ef11-9306-f0921c167864"
        ac = self.platform.get_item(ac_id, ItemType.ASSETCOLLECTION, raw=False)
        files = ["model.py", "MyExternalLibrary/functions.py"]
        ret_files = self.platform.get_files(ac, files=files, output=self.case_name)
        self.assertEqual(len(ret_files), 2)
        self._verify_files(ret_files, files)

    def test_getfiles_comps_accesscollection(self):
        ac_id = "475445f2-9359-ef11-9306-f0921c167864"
        ac = self.platform.get_item(ac_id, ItemType.ASSETCOLLECTION, raw=True)
        files = ["model.py", "MyExternalLibrary/functions.py"]
        ret_files = self.platform.get_files(ac, files=files, output=self.case_name)
        self.assertEqual(len(ret_files), 2)
        self._verify_files(ret_files, files)

    def test_get_files_by_id_accesscollection(self):
        files = ["model.py", "MyExternalLibrary/functions.py"]
        ret_files = self.platform.get_files_by_id("475445f2-9359-ef11-9306-f0921c167864",
                                                  item_type=ItemType.ASSETCOLLECTION, files=files, output=self.case_name)
        self.assertEqual(len(ret_files), 2)
        self._verify_files(ret_files, files)

    def test_getfiles_experiment(self):
        exp_id = "1e061284-d33d-f011-9310-f0921c167864"
        simulation = self.platform.get_item(exp_id, ItemType.EXPERIMENT, raw=False)
        files = ["output/result.json", "StdOut.txt"]
        with self.assertRaises(TypeError) as a:
            ret_files = self.platform.get_files(simulation, files=files, output=self.case_name)
        self.assertIn("Item Type: <class 'idmtools.entities.experiment.Experiment'> is not supported!", a.exception.args[0])

    def _verify_files(self, actual_files, expected_files):
        convert_file_path = []
        for key in actual_files.keys():
            convert_file_path.append(key.replace("\\", "/"))
        assert set(convert_file_path) == set(expected_files)
