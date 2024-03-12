import uuid
from uuid import UUID

import allure
import json
import os
import unittest

import pytest
from COMPS.Data import Experiment as COMPSExperiment, AssetCollection as CompsAssetCollection

from idmtools.assets import Asset, AssetCollection
from idmtools.core import ItemType
from idmtools.entities.experiment import Experiment
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_platform_comps.comps_platform import COMPSPlatform
from idmtools_platform_comps.utils.general import generate_ac_from_asset_id, get_asset_id
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.common_experiments import wait_on_experiment_and_check_all_sim_status
from idmtools_test.utils.comps import get_asset_collection_id_for_simulation_id, get_asset_collection_by_id, \
    setup_test_with_platform_and_simple_sweep
from idmtools_test.utils.utils import get_case_name


@pytest.mark.comps
@pytest.mark.assets
@allure.story("COMPS")
@allure.story("Assets")
@allure.suite("idmtools_platform_comps")
class TestAssetsInComps(unittest.TestCase):

    def setUp(self) -> None:
        self.base_path = os.path.abspath(os.path.join(COMMON_INPUT_PATH, "assets", "collections"))
        self.platform: COMPSPlatform = None
        self.case_name = get_case_name(os.path.basename(__file__) + "--" + self._testMethodName)
        setup_test_with_platform_and_simple_sweep(self)

    def _run_and_test_experiment(self, experiment):
        experiment.simulations.add_builder(self.builder)

        experiment.run()

        # Start experiment
        wait_on_experiment_and_check_all_sim_status(self, experiment, self.platform)

    def test_comps_asset_to_idmtools_asset(self):
        comps_ac: CompsAssetCollection = self.platform.get_item('16a032ab-bcb6-ec11-92e8-f0921c167864',
                                                                item_type=ItemType.ASSETCOLLECTION, raw=True)
        ac: AssetCollection = self.platform._assets.to_entity(comps_ac)
        self.assertIsInstance(ac, AssetCollection)

        filenames_comps = sorted(
            [f'{a.relative_path}{a.file_name}' if a.relative_path else f'{a.file_name}' for a in comps_ac.assets])
        filenames = sorted([f'{a.relative_path}{a.filename}' for a in ac.assets])
        self.assertEqual(filenames_comps, filenames)

    def test_create_asset_collection_from_existing_collection(self):
        ac = AssetCollection.from_id('16a032ab-bcb6-ec11-92e8-f0921c167864')
        self.assertIsInstance(ac, AssetCollection)
        new_ac = AssetCollection(ac.assets)
        new_ac.add_asset(Asset(relative_path=None, filename="test.json", content=json.dumps({"a": 9, "b": 2})))
        ids = self.platform.create_items([new_ac])
        new_ac = self.platform.get_item(ids[0].id, item_type=ItemType.ASSETCOLLECTION)
        self.assertIsInstance(new_ac, AssetCollection)

        filenames = set(sorted([f'{a.relative_path}{a.filename}' for a in ac.assets]))
        new_filenames = set(sorted([f'{a.relative_path}{a.filename}' for a in new_ac.assets]))

        # we should have one additional file
        self.assertEqual(len(filenames) + 1, len(new_filenames))
        # all files from original asset should be in new asset
        self.assertTrue(all([f'{a.relative_path}{a.filename}' in filenames for a in ac]))
        # the only difference should be test.json
        self.assertEqual({'test.json'}, new_filenames - filenames)

    @pytest.mark.long
    @pytest.mark.smoke
    def test_md5_hashing_for_same_file_contents(self):
        a = Asset(relative_path=None, filename="test.json", content=json.dumps({"a": 1, "b": 2}))
        b = Asset(relative_path=None, filename="test1.json", content=json.dumps({"a": 1, "b": 2}))

        ac = AssetCollection()
        ac.add_asset(a)
        ac.add_asset(b)
        ac.tags = {"string_tag": "testACtag", "number_tag": 123, "KeyOnly": None}

        model_path = os.path.join(COMMON_INPUT_PATH, "compsplatform", "working_model.py")

        task = JSONConfiguredPythonTask(script_path=model_path)
        templated_simulations = TemplatedSimulations(base_task=task)
        pe = Experiment(name=self.case_name, simulations=templated_simulations, assets=ac)

        self._run_and_test_experiment(pe)
        exp_id = pe.uid
        # exp_id = 'ae077ddd-668d-e911-a2bb-f0921c167866'
        count = 0
        test_assetcollection = []
        for simulation in COMPSExperiment.get(exp_id).get_simulations():
            collection_id = get_asset_collection_id_for_simulation_id(simulation.id)
            asset_collection = get_asset_collection_by_id(collection_id)
            if "test" in asset_collection.assets[count]._file_name:
                test_assetcollection.append(asset_collection.assets[count])
            count = count + 1

        self.assertEqual(test_assetcollection[0]._md5_checksum, test_assetcollection[1]._md5_checksum)

    def test_create_ac_from_directory_with_tags(self):
        ac = AssetCollection()
        assets_dir = os.path.join(COMMON_INPUT_PATH, "assets", "collections")
        ac.add_directory(assets_dir)
        ac.update_tags({"idmtools": "idmtools-automation", "string_tag": "testACtag", "number_tag": 123, "KeyOnly": None})

        ids = self.platform.create_items(ac)
        new_ac = self.platform.get_item(ids[0].id, item_type=ItemType.ASSETCOLLECTION)

        self.assertEqual(new_ac.tags["string_tag"], "testACtag")

    def test_create_ac_with_tags_1(self):
        a = Asset(relative_path=None, filename="test.json", content=json.dumps({"a": 1, "b": 2}))
        b = Asset(relative_path=None, filename="test1.json", content=json.dumps({"a": 1, "b": 2}))

        ac = AssetCollection(tags={"string_tag": "testACtag", "number_tag": 123, "KeyOnly": None})
        ac.add_asset(a)
        ac.add_asset(b)
        ac.update_tags({"number_tag": 321})

        ids = self.platform.create_items(ac)
        new_ac = self.platform.get_item(ids[0].id, item_type=ItemType.ASSETCOLLECTION)

        self.assertIsInstance(new_ac, AssetCollection)
        self.assertEqual(new_ac.tags["number_tag"], "321")

    def test_creat_ac_with_tags_2(self):
        a = Asset(relative_path=None, filename="test.json", content=json.dumps({"a": 1, "b": 2}))
        b = Asset(relative_path=None, filename="test1.json", content=json.dumps({"a": 1, "b": 2}))

        ac = AssetCollection()
        ac.add_asset(a)
        ac.add_asset(b)

        ac.set_tags({"string_tag": "testACtag", "number_tag": 123, "KeyOnly": None})
        ac.update_tags({"number_tag": 321})

        ids = self.platform.create_items(ac)
        new_ac = self.platform.get_item(ids[0].id, item_type=ItemType.ASSETCOLLECTION)

        self.assertIsInstance(new_ac, AssetCollection)
        self.assertEqual(new_ac.tags["number_tag"], "321")

    def test_generate_ac_from_asset_id(self):
        """
        Test that we can generate an asset collection (COMPS) from an asset id.
        """
        ac = generate_ac_from_asset_id(file_name='my_shiny_new1.sif', asset_id='8ced1fc3-cc4e-d3c5-b3fd-2919739deb2c',
                                       tags={"string_tag": "testACtag", "number_tag": 123, "KeyOnly": None})
        self.assertTrue(isinstance(ac, CompsAssetCollection))
        self.assertEqual(ac.id, UUID('b423b446-78dd-ee11-9301-f0921c167864'))
        self.assertEqual(ac.tags["string_tag"], "testACtag")

    # Handles a None value for the file_name parameter by raising a ValueError
    def test_generate_ac_from_asset_id_with_none_file_name(self):
        file_name = None
        asset_id = uuid.uuid4()

        with pytest.raises(ValueError, match=r'Invalid file_name: cannot be empty or None'):
            generate_ac_from_asset_id(file_name, asset_id)

    # Test we can not generate an asset collection (COMPS) from an unknown asset id.
    def test_generate_ac_from_asset_id_with_unknown_asset_id(self):
        file_name = "test_file"
        asset_id = uuid.uuid4()
        try:
            generate_ac_from_asset_id(file_name, asset_id)
        except Exception as e:
            assert "400 Bad Request - Unknown assets referenced in request: " in str(e)

    def test_get_same_asset_id_from_ac_id(self):
        # below specific ac_id will return 4 files with different filenames, but they are all empty. so md5_checksum or
        # asset_id should be the same
        ac_id = "54b72e0f-98e0-ee11-9301-f0921c167864"

        result = get_asset_id(ac_id)

        assert isinstance(result, dict)
        assert len(result) == 4
        assert all(v == UUID("d41d8cd9-8f00-b204-e980-0998ecf8427e") for v in result.values())

    def test_get_asset_id_from_ac_id(self):
        # below specific ac_id will return 3 files with different filenames and different md5_checksums
        ac_id = "19c42d1a-d0df-ee11-9301-f0921c167864"

        result = get_asset_id(ac_id)

        assert isinstance(result, dict)
        assert len(result) == 3

        expected_dict = {
            "dtk_run_rocky_py39.sif": UUID("ffae6e06-d3bf-29c2-868f-44168f078212"),
            "Eradication": UUID("f1b0c477-2f19-7ed2-e22c-c2893c82657b"),
            "demographics.json": UUID("0f4710cb-42e9-2666-3cc2-9251c4b36726")
        }
        self.assertDictEqual(result, expected_dict)

    def test_get_asset_id_from_ac_id_with_unknown_ac_id(self):
        ac_id = "unknown_ac_id"

        with pytest.raises(ValueError, match=f'Invalid id: {ac_id}'):
            get_asset_id(ac_id)


if __name__ == '__main__':
    unittest.main()
