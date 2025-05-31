import unittest
from idmtools.assets import AssetCollection
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.entities.generic_workitem import GenericWorkItem
from idmtools.entities.simulation import Simulation
from COMPS.Data import Simulation as COMPSSimulation
from COMPS.Data import WorkItem as COMPSWorkItem
from COMPS.Data import AssetCollection as COMPSAssetCollection


class TestFlattenItem(unittest.TestCase):
    def setUp(self):
        self.platform = Platform('SlurmStage')

    def test_flatten_item_suite_true_true(self):
        suite_id = "c47cbc8c-e43c-f011-9310-f0921c167864"
        exp = self.platform.get_item(suite_id, ItemType.SUITE, raw=True)
        sims = self.platform.flatten_item(exp, raw=False)
        self.assertTrue(len(sims), 5)
        self.assertTrue(all(isinstance(item, Simulation) for item in sims))

    def test_flatten_item_suite_true_false(self):
        suite_id = "c47cbc8c-e43c-f011-9310-f0921c167864"
        exp = self.platform.get_item(suite_id, ItemType.SUITE, raw=True)
        sims = self.platform.flatten_item(exp, raw=True)
        self.assertTrue(len(sims), 5)
        self.assertTrue(all(isinstance(item, COMPSSimulation) for item in sims))

    def test_flatten_item_suite_false_false(self):
        suite_id = "c47cbc8c-e43c-f011-9310-f0921c167864"
        exp = self.platform.get_item(suite_id, ItemType.SUITE)
        sims = self.platform.flatten_item(exp, raw=False)
        self.assertTrue(len(sims), 5)
        self.assertTrue(all(isinstance(item, Simulation) for item in sims))

    def test_flatten_item_suite_false_true(self):
        suite_id = "c47cbc8c-e43c-f011-9310-f0921c167864"
        exp = self.platform.get_item(suite_id, ItemType.SUITE)
        sims = self.platform.flatten_item(exp, raw=True)
        self.assertTrue(len(sims), 5)
        self.assertTrue(all(isinstance(item, COMPSSimulation) for item in sims))

    def test_flatten_item_exp_true_true(self):
        exp_id = "69cab2fe-a252-ea11-a2bf-f0921c167862"
        exp = self.platform.get_item(exp_id, ItemType.EXPERIMENT, raw=True)
        sims = self.platform.flatten_item(exp, raw=False)
        self.assertTrue(len(sims), 5)
        self.assertTrue(all(isinstance(item, Simulation) for item in sims))

    def test_flatten_item_exp_true_false(self):
        exp_id = "69cab2fe-a252-ea11-a2bf-f0921c167862"
        exp = self.platform.get_item(exp_id, ItemType.EXPERIMENT, raw=True)
        sims = self.platform.flatten_item(exp, raw=True)
        self.assertTrue(len(sims), 5)
        self.assertTrue(all(isinstance(item, COMPSSimulation) for item in sims))

    def test_flatten_item_exp_false_false(self):
        exp_id = "69cab2fe-a252-ea11-a2bf-f0921c167862"
        exp = self.platform.get_item(exp_id, ItemType.EXPERIMENT)
        sims = self.platform.flatten_item(exp, raw=False)
        self.assertTrue(len(sims), 5)
        self.assertTrue(all(isinstance(item, Simulation) for item in sims))

    def test_flatten_item_exp_false_true(self):
        exp_id = "69cab2fe-a252-ea11-a2bf-f0921c167862"
        exp = self.platform.get_item(exp_id, ItemType.EXPERIMENT)
        sims = self.platform.flatten_item(exp, raw=True)
        self.assertTrue(len(sims), 5)
        self.assertTrue(all(isinstance(item, COMPSSimulation) for item in sims))

    def test_flatten_item_sim_true_true(self):
        sim_id = "c97cbc8c-e43c-f011-9310-f0921c167864"
        sim = self.platform.get_item(sim_id, ItemType.SIMULATION, raw=True)
        sims = self.platform.flatten_item(sim, raw=True)
        self.assertTrue(len(sims), 1)
        self.assertTrue(all(isinstance(item, COMPSSimulation) for item in sims))

    def test_flatten_item_sim_true_false(self):
        sim_id = "c97cbc8c-e43c-f011-9310-f0921c167864"
        sim = self.platform.get_item(sim_id, ItemType.SIMULATION, raw=True)
        sims = self.platform.flatten_item(sim, raw=False)
        self.assertTrue(len(sims), 1)
        self.assertTrue(all(isinstance(item, Simulation) for item in sims))

    def test_flatten_item_sim_false_false(self):
        sim_id = "c97cbc8c-e43c-f011-9310-f0921c167864"
        sim = self.platform.get_item(sim_id, ItemType.SIMULATION)
        sims = self.platform.flatten_item(sim, raw=False)
        self.assertTrue(len(sims), 5)
        self.assertTrue(all(isinstance(item, Simulation) for item in sims))

    def test_flatten_item_sim_false_true(self):
        sim_id = "c97cbc8c-e43c-f011-9310-f0921c167864"
        sim = self.platform.get_item(sim_id, ItemType.SIMULATION)
        sims = self.platform.flatten_item(sim, raw=True)
        self.assertTrue(len(sims), 1)
        self.assertTrue(all(isinstance(item, COMPSSimulation) for item in sims))

    def test_flatten_item_workitem_true_true(self):
        workitem_id = "7ad3f7b8-063d-f011-9310-f0921c167864"
        workitem = self.platform.get_item(workitem_id, ItemType.WORKFLOW_ITEM, raw=True)
        workitems = self.platform.flatten_item(workitem, raw=True)
        self.assertTrue(len(workitems), 1)
        self.assertTrue(isinstance(workitems[0], COMPSWorkItem))

    def test_flatten_item_workitem_true_false(self):
        workitem_id = "7ad3f7b8-063d-f011-9310-f0921c167864"
        workitem = self.platform.get_item(workitem_id, ItemType.WORKFLOW_ITEM, raw=True)
        workitems = self.platform.flatten_item(workitem, raw=False)
        self.assertTrue(len(workitems), 1)
        self.assertTrue(isinstance(workitems[0], GenericWorkItem))

    def test_flatten_item_workitem_false_false(self):
        workitem_id = "7ad3f7b8-063d-f011-9310-f0921c167864"
        workitem = self.platform.get_item(workitem_id, ItemType.WORKFLOW_ITEM)
        workitems = self.platform.flatten_item(workitem, raw=False)
        self.assertTrue(len(workitems), 1)
        self.assertTrue(isinstance(workitems[0], GenericWorkItem))

    def test_flatten_item_workitem_false_true(self):
        workitem_id = "7ad3f7b8-063d-f011-9310-f0921c167864"
        workitem = self.platform.get_item(workitem_id, ItemType.WORKFLOW_ITEM, raw=False)
        workitems = self.platform.flatten_item(workitem, raw=True)
        self.assertTrue(len(workitems), 1)
        self.assertTrue(isinstance(workitems[0], COMPSWorkItem))

    def test_flatten_item_ac_true_true(self):
        ac_id = "ca2c7680-5a5f-eb11-a2c2-f0921c167862"
        asset_collection = self.platform.get_item(ac_id, ItemType.ASSETCOLLECTION, raw=True)
        asset_collections = self.platform.flatten_item(asset_collection, raw=True)
        self.assertTrue(len(asset_collections), 1)
        self.assertTrue(isinstance(asset_collections[0], COMPSAssetCollection))

    def test_flatten_item_ac_true_false(self):
        ac_id = "ca2c7680-5a5f-eb11-a2c2-f0921c167862"
        asset_collection = self.platform.get_item(ac_id, ItemType.ASSETCOLLECTION, raw=True)
        asset_collections = self.platform.flatten_item(asset_collection, raw=False)
        self.assertTrue(len(asset_collections), 1)
        self.assertTrue(isinstance(asset_collections[0], AssetCollection))

    def test_flatten_item_ac_false_false(self):
        ac_id = "ca2c7680-5a5f-eb11-a2c2-f0921c167862"
        asset_collection = self.platform.get_item(ac_id, ItemType.ASSETCOLLECTION)
        asset_collections = self.platform.flatten_item(asset_collection, raw=False)
        self.assertTrue(len(asset_collections), 1)
        self.assertTrue(isinstance(asset_collections[0], AssetCollection))

    def test_flatten_item_ac_false_true(self):
        ac_id = "ca2c7680-5a5f-eb11-a2c2-f0921c167862"
        asset_collection = self.platform.get_item(ac_id, ItemType.ASSETCOLLECTION)
        asset_collections = self.platform.flatten_item(asset_collection, raw=True)
        self.assertTrue(len(asset_collections), 1)
        self.assertTrue(isinstance(asset_collections[0], COMPSAssetCollection))
