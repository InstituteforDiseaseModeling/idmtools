import json
import os
import pytest
import unittest
from COMPS.Data import Experiment
from idmtools.assets import Asset, AssetCollection
from idmtools.core import EntityStatus
from idmtools_models.python import PythonExperiment
from idmtools_platform_comps.comps_platform import COMPSPlatform
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.comps import get_asset_collection_id_for_simulation_id, get_asset_collection_by_id, \
    assure_running_then_wait_til_done, setup_test_with_platform_and_simple_sweep


@pytest.mark.comps
@pytest.mark.assets
class TestAssetsInComps(unittest.TestCase):

    def setUp(self) -> None:
        self.base_path = os.path.abspath(os.path.join(COMMON_INPUT_PATH, "assets", "collections"))
        self.platform: COMPSPlatform = None
        setup_test_with_platform_and_simple_sweep(self)

    def _run_and_test_experiment(self, experiment):
        experiment.builder = self.builder
        experiment.platform = self.platform

        # Create experiment on platform
        experiment.pre_creation()
        self.platform.create_items(items=[experiment])

        for simulation_batch in experiment.batch_simulations(batch_size=10):
            # Create the simulations on the platform
            for simulation in simulation_batch:
                simulation.pre_creation()

            ids = self.platform.create_items(items=simulation_batch)

            for uid, simulation in zip(ids, simulation_batch):
                simulation.uid = uid
                simulation.post_creation()

                experiment.simulations.append(simulation.metadata)
                experiment.simulations.set_status(EntityStatus.CREATED)

                from idmtools.entities import ISimulation
                simulation.__class__ = ISimulation

        self.platform.refresh_status(item=experiment)

        # Test if we have all simulations at status CREATED
        self.assertFalse(experiment.done)
        self.assertTrue(all([s.status == EntityStatus.CREATED for s in experiment.simulations]))

        # Start experiment
        assure_running_then_wait_til_done(self, experiment)

    @pytest.mark.long
    def test_md5_hashing_for_same_file_contents(self):
        a = Asset(relative_path=None, filename="test.json", content=json.dumps({"a": 1, "b": 2}))
        b = Asset(relative_path=None, filename="test1.json", content=json.dumps({"a": 1, "b": 2}))

        ac = AssetCollection()
        ac.add_asset(a)
        ac.add_asset(b)
        ac.tags = {"idmtools": "idmtools-automation", "string_tag": "testACtag", "number_tag": 123, "KeyOnly": None}

        pe = PythonExperiment(name=self.case_name,
                              model_path=os.path.join(COMMON_INPUT_PATH, "compsplatform", "working_model.py"),
                              assets=ac)
        pe.tags = {"idmtools": "idmtools-automation"}
        pe.platform = self.platform
        self._run_and_test_experiment(pe)
        exp_id = pe.uid
        # exp_id = 'ae077ddd-668d-e911-a2bb-f0921c167866'
        for simulation in Experiment.get(exp_id).get_simulations():
            collection_id = get_asset_collection_id_for_simulation_id(simulation.id)
            asset_collection = get_asset_collection_by_id(collection_id)
            self.assertEqual(asset_collection.assets[0]._md5_checksum, asset_collection.assets[1]._md5_checksum)
            self.assertEqual(asset_collection.assets[0]._file_name, 'test.json')
            self.assertEqual(asset_collection.assets[1]._file_name, 'test1.json')

    # TODO: test is incomplete
    # def test_create_asset_collection(self):
    #     ac = AssetCollection()
    #     assets_dir = os.path.join(COMMON_INPUT_PATH, "assets", "collections")
    #     ac.assets_from_directory(assets_dir)
    #     # add tags to ACs - can't currently do this
    #     ac.tags = {"idmtools": "idmtools-automation", "string_tag": "testACtag", "number_tag": 123, "KeyOnly": None}
    #
    #     self.assertSetEqual(set(ac.assets), set(AssetCollection.tags))


if __name__ == '__main__':
    unittest.main()
