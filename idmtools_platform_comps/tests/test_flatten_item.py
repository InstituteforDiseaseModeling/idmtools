import unittest
import uuid
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

    def test_flatten_item_suite_true_false(self):
        suite_id = "c47cbc8c-e43c-f011-9310-f0921c167864"
        suite = self.platform.get_item(suite_id, ItemType.SUITE, raw=True)
        sims = self.platform.flatten_item(suite, raw=False)
        self.assertEqual(len(sims), 5)
        self.assertTrue(all(isinstance(item, Simulation) for item in sims))
        self._verify_idm_extra_fields(sims)

    def test_flatten_item_suite_true_true(self):
        suite_id = "c47cbc8c-e43c-f011-9310-f0921c167864"
        suite = self.platform.get_item(suite_id, ItemType.SUITE, raw=True)
        sims = self.platform.flatten_item(suite, raw=True)
        self.assertEqual(len(sims), 5)
        self.assertTrue(all(isinstance(item, COMPSSimulation) for item in sims))
        self._verify_idm_extra_fields(sims)

    def test_flatten_item_suite_false_false(self):
        suite_id = "c47cbc8c-e43c-f011-9310-f0921c167864"
        suite = self.platform.get_item(suite_id, ItemType.SUITE)
        sims = self.platform.flatten_item(suite, raw=False)
        self.assertEqual(len(sims), 5)
        self.assertTrue(all(isinstance(item, Simulation) for item in sims))
        self._verify_idm_extra_fields(sims)

    def test_flatten_item_suite_false_true(self):
        suite_id = "c47cbc8c-e43c-f011-9310-f0921c167864"
        suite = self.platform.get_item(suite_id, ItemType.SUITE)
        sims = self.platform.flatten_item(suite, raw=True)
        self.assertEqual(len(sims), 5)
        self.assertTrue(all(isinstance(item, COMPSSimulation) for item in sims))
        self._verify_idm_extra_fields(sims)

    def test_flatten_item_exp_true_false(self):
        exp_id = "69cab2fe-a252-ea11-a2bf-f0921c167862"
        exp = self.platform.get_item(exp_id, ItemType.EXPERIMENT, raw=True)
        sims = self.platform.flatten_item(exp, raw=False)
        self.assertEqual(len(sims), 6)
        self.assertTrue(all(isinstance(item, Simulation) for item in sims))
        self._verify_idm_extra_fields(sims)

    def test_flatten_item_exp_true_true(self):
        exp_id = "69cab2fe-a252-ea11-a2bf-f0921c167862"
        exp = self.platform.get_item(exp_id, ItemType.EXPERIMENT, raw=True)
        sims = self.platform.flatten_item(exp, raw=True)
        self.assertTrue(len(sims), 6)
        self.assertTrue(all(isinstance(item, COMPSSimulation) for item in sims))
        self._verify_idm_extra_fields(sims)

    def test_flatten_item_exp_false_false(self):
        exp_id = "69cab2fe-a252-ea11-a2bf-f0921c167862"
        exp = self.platform.get_item(exp_id, ItemType.EXPERIMENT)
        sims = self.platform.flatten_item(exp, raw=False)
        self.assertEqual(len(sims), 6)
        self.assertTrue(all(isinstance(item, Simulation) for item in sims))
        self._verify_idm_extra_fields(sims)

    def test_flatten_item_exp_false_true(self):
        exp_id = "69cab2fe-a252-ea11-a2bf-f0921c167862"
        exp = self.platform.get_item(exp_id, ItemType.EXPERIMENT)
        sims = self.platform.flatten_item(exp, raw=True)
        self.assertEqual(len(sims), 6)
        self.assertTrue(all(isinstance(item, COMPSSimulation) for item in sims))
        self._verify_idm_extra_fields(sims)

    def test_flatten_item_sim_true_true(self):
        sim_id = "c97cbc8c-e43c-f011-9310-f0921c167864"
        sim = self.platform.get_item(sim_id, ItemType.SIMULATION, raw=True)
        sims = self.platform.flatten_item(sim, raw=True)
        self.assertEqual(len(sims), 1)
        self.assertTrue(all(isinstance(item, COMPSSimulation) for item in sims))
        self._verify_idm_extra_fields(sims)

    def test_flatten_item_sim_true_false(self):
        sim_id = "c97cbc8c-e43c-f011-9310-f0921c167864"
        sim = self.platform.get_item(sim_id, ItemType.SIMULATION, raw=True)
        sims = self.platform.flatten_item(sim, raw=False)
        self.assertEqual(len(sims), 1)
        self.assertTrue(all(isinstance(item, Simulation) for item in sims))
        self._verify_idm_extra_fields(sims)

    def test_flatten_item_sim_false_false(self):
        sim_id = "c97cbc8c-e43c-f011-9310-f0921c167864"
        sim = self.platform.get_item(sim_id, ItemType.SIMULATION)
        sims = self.platform.flatten_item(sim, raw=False)
        self.assertEqual(len(sims), 1)
        self.assertTrue(all(isinstance(item, Simulation) for item in sims))
        self.assertEqual(sims[0], sim)

    def test_flatten_item_sim_false_true(self):
        sim_id = "c97cbc8c-e43c-f011-9310-f0921c167864"
        sim = self.platform.get_item(sim_id, ItemType.SIMULATION)
        sims = self.platform.flatten_item(sim, raw=True)
        self.assertEqual(len(sims), 1)
        self.assertTrue(all(isinstance(item, COMPSSimulation) for item in sims))
        self._verify_idm_extra_fields(sims)

    def test_flatten_item_workitem_true_true(self):
        workitem_id = "7ad3f7b8-063d-f011-9310-f0921c167864"
        workitem = self.platform.get_item(workitem_id, ItemType.WORKFLOW_ITEM, raw=True)
        workitems = self.platform.flatten_item(workitem, raw=True)
        self.assertEqual(len(workitems), 1)
        self.assertTrue(isinstance(workitems[0], COMPSWorkItem))
        self._verify_idm_extra_fields(workitems)

    def test_flatten_item_workitem_true_false(self):
        workitem_id = "7ad3f7b8-063d-f011-9310-f0921c167864"
        workitem = self.platform.get_item(workitem_id, ItemType.WORKFLOW_ITEM, raw=True)
        workitems = self.platform.flatten_item(workitem, raw=False)
        self.assertEqual(len(workitems), 1)
        self.assertTrue(isinstance(workitems[0], GenericWorkItem))
        self._verify_idm_extra_fields(workitems)

    def test_flatten_item_workitem_false_false(self):
        workitem_id = "7ad3f7b8-063d-f011-9310-f0921c167864"
        workitem = self.platform.get_item(workitem_id, ItemType.WORKFLOW_ITEM)
        workitems = self.platform.flatten_item(workitem, raw=False)
        self.assertTrue(isinstance(workitems[0], GenericWorkItem))
        self.assertEqual(len(workitems), 1)
        self.assertEqual(workitems[0], workitem)

    def test_flatten_item_workitem_false_true(self):
        workitem_id = "7ad3f7b8-063d-f011-9310-f0921c167864"
        workitem = self.platform.get_item(workitem_id, ItemType.WORKFLOW_ITEM, raw=False)
        workitems = self.platform.flatten_item(workitem, raw=True)
        self.assertEqual(len(workitems), 1)
        self.assertTrue(isinstance(workitems[0], COMPSWorkItem))
        self._verify_idm_extra_fields(workitems)

    def test_flatten_item_ac_true_true(self):
        ac_id = "ca2c7680-5a5f-eb11-a2c2-f0921c167862"
        asset_collection = self.platform.get_item(ac_id, ItemType.ASSETCOLLECTION, raw=True)
        asset_collections = self.platform.flatten_item(asset_collection, raw=True)
        self.assertEqual(len(asset_collections), 1)
        self.assertTrue(isinstance(asset_collections[0], COMPSAssetCollection))
        self._verify_idm_extra_fields(asset_collections)

    def test_flatten_item_ac_true_false(self):
        ac_id = "ca2c7680-5a5f-eb11-a2c2-f0921c167862"
        asset_collection = self.platform.get_item(ac_id, ItemType.ASSETCOLLECTION, raw=True)
        asset_collections = self.platform.flatten_item(asset_collection, raw=False)
        self.assertEqual(len(asset_collections), 1)
        self.assertTrue(isinstance(asset_collections[0], AssetCollection))
        self._verify_idm_extra_fields(asset_collections)

    def test_flatten_item_ac_false_false(self):
        ac_id = "ca2c7680-5a5f-eb11-a2c2-f0921c167862"
        asset_collection = self.platform.get_item(ac_id, ItemType.ASSETCOLLECTION)
        asset_collections = self.platform.flatten_item(asset_collection, raw=False)
        self.assertEqual(len(asset_collections), 1)
        self.assertTrue(isinstance(asset_collections[0], AssetCollection))
        self.assertEqual(asset_collections[0], asset_collection)

    def test_flatten_item_ac_false_true(self):
        ac_id = "ca2c7680-5a5f-eb11-a2c2-f0921c167862"
        asset_collection = self.platform.get_item(ac_id, ItemType.ASSETCOLLECTION)
        asset_collections = self.platform.flatten_item(asset_collection, raw=True)
        self.assertEqual(len(asset_collections), 1)
        self.assertTrue(isinstance(asset_collections[0], COMPSAssetCollection))
        self._verify_idm_extra_fields(asset_collections)

    def _verify_idm_extra_fields(self, items):
        for item in items:
            self.assertTrue(isinstance(item.id, str))
            self.assertEqual(str(item.uid), item.id)
            if isinstance(item, (COMPSSimulation, COMPSWorkItem, COMPSAssetCollection)):
                self.assertTrue(isinstance(item.uid, uuid.UUID))  # uid is UUID when item is server item
            else:
                self.assertTrue(isinstance(item.uid, str))  # uid is string type when item is not server item

    def test_get_directory(self):
        suite_id = "c47cbc8c-e43c-f011-9310-f0921c167864"
        suite = self.platform.get_item(suite_id, ItemType.SUITE, raw=True)
        sims = self.platform.flatten_item(suite, raw=True)
        # Test get_directory for comps object
        # First test simulation.get_directory()
        try:
            sims[0].get_directory()
        except Exception as e:
            self.assertTrue("'Simulation' object has no attribute 'get_directory'" in str(e))
        # test platform.get_directory(simulation)
        try:
            self.platform.get_directory(sims[0])
        except Exception as e:
            self.assertTrue("'COMPSPlatform' object has no attribute 'get_directory'" in str(e))