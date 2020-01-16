import copy
import json
import os
import pytest
import unittest
from functools import partial
from operator import itemgetter
from COMPS.Data import Experiment
from idmtools.assets import Asset, AssetCollection
from idmtools.builders import ArmExperimentBuilder, ArmType, ExperimentBuilder, StandAloneSimulationsBuilder, SweepArm
from idmtools.core.platform_factory import Platform
from idmtools.managers import ExperimentManager
from idmtools_models.python import PythonExperiment
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools_test.utils.comps import get_asset_collection_id_for_simulation_id, get_asset_collection_by_id
from idmtools_test import COMMON_INPUT_PATH
from idmtools.core import EntityStatus, ItemType
from COMPS.Data import QueryCriteria


def param_update(simulation, param, value):
    return simulation.set_parameter(param, value)


setA = partial(param_update, param="a")
setB = partial(param_update, param="b")
setC = partial(param_update, param="c")


class setParam:
    def __init__(self, param):
        self.param = param

    def __call__(self, simulation, value):
        return param_update(simulation, self.param, value)


@pytest.mark.comps
@pytest.mark.python
class TestPythonExperiment(ITestWithPersistence):
    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        print(self.case_name)
        self.platform = Platform('COMPS2')

    # Test 2 ways to sweep parameters
    # First way: use partial function
    # Second way: define a setParam class and __call__ method
    # Also current add_sweep_definition will do product of each call. if first call has 5 parameters, second call also
    # has 5 parameter, total sweep parameters are 5*5=25

    @pytest.mark.long
    def test_sweeps_with_partial_comps(self):
        pe = PythonExperiment(name=self.case_name, model_path=os.path.join(COMMON_INPUT_PATH, "python", "model1.py"))

        pe.tags = {"idmtools": "idmtools-automation", "string_tag": "test", "number_tag": 123, "KeyOnly": None}
        pe.base_simulation.set_parameter("c", "c-value")
        builder = ExperimentBuilder()
        # ------------------------------------------------------
        # Sweeping parameters:
        # first way to sweep parameter 'a' is to use param_update function
        builder.add_sweep_definition(setA, range(0, 2))

        # second way to sweep parameter 'b' is to use class setParam which basiclly doing same thing as param_update mathod
        builder.add_sweep_definition(setParam("b"), [i * i for i in range(1, 4, 2)])
        # ------------------------------------------------------

        pe.builder = builder

        em = ExperimentManager(experiment=pe, platform=self.platform)
        em.run()
        em.wait_till_done()
        self.assertTrue(all([s.status == EntityStatus.SUCCEEDED for s in pe.simulations]))
        experiment = Experiment.get(em.experiment.uid)
        print(experiment.id)
        exp_id = experiment.id
        # exp_id = "a727e802-d88b-e911-a2bb-f0921c167866"

        # validation each simulation output to compare output/config.json is equal to config.json
        self.validate_output(exp_id, 4)

        expected_tags = [{'a': '0', 'b': '1'}, {'a': '0', 'b': '9'}, {'a': '1', 'b': '1'}, {'a': '1', 'b': '9'}]
        self.validate_sim_tags(exp_id, expected_tags)

        # validate experiment tags
        actual_exp_tags = experiment.get(experiment.id, QueryCriteria().select_children('tags')).tags
        expected_exp_tags = {'idmtools': 'idmtools-automation', 'number_tag': '123', 'string_tag': 'test',
                             'KeyOnly': '', 'type': 'idmtools_models.python.python_experiment.PythonExperiment'}
        self.assertDictEqual(expected_exp_tags, actual_exp_tags)

    # Test parameter "b" set is depending on parameter "a"
    # a=[0,1,2,3,4] <--sweep parameter
    # b=[2,3,4,5,6]  <-- b = a + 2
    @pytest.mark.long
    def test_sweeps_2_related_parameters_comps(self):
        pe = PythonExperiment(name=self.case_name, model_path=os.path.join(COMMON_INPUT_PATH, "python", "model1.py"))
        pe.tags = {"idmtools": "idmtools-automation", "string_tag": "test", "number_tag": 123}

        pe.base_simulation.set_parameter("c", "c-value")

        def param_update_ab(simulation, param, value):
            # Set B within
            if param == "a":
                simulation.set_parameter("b", value + 2)

            return simulation.set_parameter(param, value)

        setAB = partial(param_update_ab, param="a")

        builder = ExperimentBuilder()
        # Sweep parameter "a" and make "b" depends on "a"
        builder.add_sweep_definition(setAB, range(0, 5))
        pe.builder = builder
        em = ExperimentManager(experiment=pe, platform=self.platform)
        em.run()
        em.wait_till_done()
        self.assertTrue(all([s.status == EntityStatus.SUCCEEDED for s in pe.simulations]))
        experiment = Experiment.get(em.experiment.uid)
        print(experiment.id)
        exp_id = experiment.id
        self.validate_output(exp_id, 5)

        # validate b is not in tag since it is not sweep parameter, it just depend on sweep parameter
        expected_tags = [{'a': '0'}, {'a': '1'}, {'a': '2'}, {'a': '3'}, {'a': '4'}]
        self.validate_sim_tags(exp_id, expected_tags)

    @pytest.mark.long
    @pytest.mark.comps
    def test_add_prefixed_relative_path_to_assets_comps(self):
        model_path = os.path.join(COMMON_INPUT_PATH, "python", "model.py")
        ac = AssetCollection()
        assets_path = os.path.join(COMMON_INPUT_PATH, "python", "Assets", "MyExternalLibrary")
        ac.add_directory(assets_directory=assets_path, relative_path="MyExternalLibrary")
        pe = PythonExperiment(name=self.case_name, model_path=model_path, assets=ac)
        # assets=AssetCollection.from_directory(assets_directory=assets_path, relative_path="MyExternalLibrary"))
        pe.tags = {"idmtools": "idmtools-automation", "string_tag": "test", "number_tag": 123}
        pe.base_simulation.envelope = "parameters"

        pe.base_simulation.set_parameter("b", 10)

        def param_a_update(simulation, value):
            simulation.set_parameter("a", value)
            return {"a": value}

        builder = ExperimentBuilder()
        # Sweep parameter "a"
        builder.add_sweep_definition(param_a_update, range(0, 2))
        pe.builder = builder
        em = ExperimentManager(experiment=pe, platform=self.platform)
        em.run()
        em.wait_till_done()
        self.assertTrue(all([s.status == EntityStatus.SUCCEEDED for s in pe.simulations]))
        exp_id = em.experiment.uid
        # exp_id ='ef8e7f2f-a793-e911-a2bb-f0921c167866'
        count = 0
        for simulation in Experiment.get(exp_id).get_simulations():
            # validate output/config.json
            config_string = simulation.retrieve_output_files(paths=["config.json"])
            config_parameters = json.loads(config_string[0].decode('utf-8'))['parameters']
            self.assertEqual(config_parameters["a"], count)
            self.assertEqual(config_parameters["b"], 10)
            count = count + 1

            # validate Assets files
            collection_id = get_asset_collection_id_for_simulation_id(simulation.id)
            asset_collection = get_asset_collection_by_id(collection_id)
            assets = asset_collection.assets
            self.assertEqual(len(assets), 3)

            expected_list = [{'filename': '__init__.py', 'relative_path': 'MyExternalLibrary'},
                             {'filename': 'model.py', 'relative_path': ''},
                             {'filename': 'functions.py', 'relative_path': 'MyExternalLibrary'}]
            self.validate_assets(assets, expected_list)

    # Test will test pythonExperiment's assets parameter which adds all files under tests/inputs/python/Assets to
    # COMPS' Assets folder and also test using StandAloneSimulationsBuilder builder to build simulations
    # Comps' Assets
    #   |--MyLib
    #       |--temp.py
    #   |--MyExternalLibrary
    #       |--__init__.py
    #       |--functions.py
    #   |--__init__.py
    #   |--model.py
    @pytest.mark.long
    @pytest.mark.comps
    def test_add_dirs_to_assets_comps(self):
        model_path = os.path.join(COMMON_INPUT_PATH, "python", "model.py")
        ac = AssetCollection()
        assets_path = os.path.join(COMMON_INPUT_PATH, "python", "Assets")
        ac.add_directory(assets_directory=assets_path)
        pe = PythonExperiment(name=self.case_name, model_path=model_path, assets=ac)
        pe.tags = {"idmtools": "idmtools-automation", "string_tag": "test", "number_tag": 123}
        pe.base_simulation.envelope = "parameters"
        # sim = pe.simulation() # uncomment this line when issue #138 gets fixed
        sim = pe.simulation()
        sim.set_parameter("a", 1)
        sim.set_parameter("b", 10)
        builder = StandAloneSimulationsBuilder()
        builder.add_simulation(sim)
        pe.builder = builder
        em = ExperimentManager(experiment=pe, platform=self.platform)
        em.run()
        em.wait_till_done()
        self.assertTrue(all([s.status == EntityStatus.SUCCEEDED for s in pe.simulations]))
        exp_id = em.experiment.uid
        # validate results from comps
        # exp_id ='eb7ce224-9993-e911-a2bb-f0921c167866'
        for simulation in Experiment.get(exp_id).get_simulations():
            # validate output/config.json
            assets = self.assert_valid_config_stdout_and_assets(simulation)
            self.assertEqual(len(assets), 5)

            expected_list = [{'filename': '__init__.py', 'relative_path': 'MyExternalLibrary'},
                             {'filename': '__init__.py', 'relative_path': ''},
                             {'filename': 'model.py', 'relative_path': ''},
                             {'filename': 'temp.py', 'relative_path': 'MyLib'},
                             {'filename': 'functions.py', 'relative_path': 'MyExternalLibrary'}]
            self.validate_assets(assets, expected_list)

    def assert_valid_config_stdout_and_assets(self, simulation):
        config_string = simulation.retrieve_output_files(paths=["config.json"])
        config_parameters = json.loads(config_string[0].decode('utf-8'))['parameters']
        self.assertEqual(config_parameters["a"], 1)
        self.assertEqual(config_parameters["b"], 10)
        # validate StdOut.txt
        stdout = simulation.retrieve_output_files(paths=["StdOut.txt"])
        self.assertEqual(stdout, [b"11\r\n{'a': 1, 'b': 10}\r\n"])
        # validate Assets files
        collection_id = get_asset_collection_id_for_simulation_id(simulation.id)
        asset_collection = get_asset_collection_by_id(collection_id)
        assets = asset_collection.assets
        return assets

    def assert_valid_new_assets(self, simulation):
        config_string = simulation.retrieve_output_files(paths=["config.json"])
        config_parameters = json.loads(config_string[0].decode('utf-8'))['parameters']
        self.assertGreaterEqual(config_parameters["min_x"], -2)
        self.assertLessEqual(config_parameters["min_x"], 1)
        self.assertGreaterEqual(config_parameters["max_x"], -2)
        self.assertLessEqual(config_parameters["max_x"], 2)
        # validate Assets files
        collection_id = get_asset_collection_id_for_simulation_id(simulation.id)
        asset_collection = get_asset_collection_by_id(collection_id)
        assets = asset_collection.assets
        return assets

    def assert_same_asset_id(self, simulation):
        collection_id = get_asset_collection_id_for_simulation_id(simulation.id)
        return collection_id

    # Test will test pythonExperiment's assets parameter which adds only specific file under
    # tests/inputs/python/Assets/MyExternalLibrary to COMPS' Assets and add relative_path MyExternalLibrary in comps
    # Comps' Assets
    #   |--MyExternalLibrary
    #       |--functions.py
    #   |--model.py
    @pytest.mark.long
    @pytest.mark.comps
    def test_add_specific_files_to_assets_comps(self):
        model_path = os.path.join(COMMON_INPUT_PATH, "python", "model.py")
        ac = AssetCollection()
        a = Asset(relative_path="MyExternalLibrary",
                  absolute_path=os.path.join(COMMON_INPUT_PATH, "python", "Assets", "MyExternalLibrary",
                                             "functions.py"))
        ac.add_asset(a)
        pe = PythonExperiment(name=self.case_name, model_path=model_path, assets=ac)
        pe.tags = {"idmtools": "idmtools-automation", "string_tag": "test", "number_tag": 123}
        pe.base_simulation.set_parameter("a", 1)
        pe.base_simulation.set_parameter("b", 10)
        pe.base_simulation.envelope = "parameters"
        em = ExperimentManager(experiment=pe, platform=self.platform)
        em.run()
        em.wait_till_done()
        self.assertTrue(all([s.status == EntityStatus.SUCCEEDED for s in pe.simulations]))
        exp_id = em.experiment.uid
        # validate results from comps
        # exp_id ='a98090dc-ea92-e911-a2bb-f0921c167866'
        for simulation in Experiment.get(exp_id).get_simulations():
            # validate output/config.json
            assets = self.assert_valid_config_stdout_and_assets(simulation)
            self.assertEqual(len(assets), 2)
            expected_list = [{'filename': 'functions.py', 'relative_path': 'MyExternalLibrary'},
                             {'filename': 'model.py', 'relative_path': ''}]
            self.validate_assets(assets, expected_list)

    # |__ A = 1
    #      |_ B = [2,3]
    #      |_ C = [4,5]
    # |__ A = [6,7]
    #    |_ B = 2
    # expect sims with parameters:
    # {1,2,4}
    # {1,2,5}
    # {1,3,4}
    # {1,3,5}
    # {6,2}
    # {7,2}
    @pytest.mark.comps
    @pytest.mark.long
    def test_sweep_in_arms_cross(self):
        pe = PythonExperiment(name=self.case_name,
                              model_path=os.path.join(COMMON_INPUT_PATH, "python", "model1.py"))
        pe.tags = {"idmtools": "idmtools-automation", "string_tag": "test", "number_tag": 123, "KeyOnly": None}

        arm = SweepArm(type=ArmType.cross)
        builder = ArmExperimentBuilder()
        arm.add_sweep_definition(setA, 1)
        arm.add_sweep_definition(setB, [2, 3])
        arm.add_sweep_definition(setC, [4, 5])
        builder.add_arm(arm)
        arm = SweepArm(type=ArmType.cross)
        arm.add_sweep_definition(setA, [6, 7])
        arm.add_sweep_definition(setB, [2])
        builder.add_arm(arm)
        pe.builder = builder
        em = ExperimentManager(experiment=pe, platform=self.platform)
        em.run()
        em.wait_till_done()
        exp_id = em.experiment.uid
        self.assertTrue(all([s.status == EntityStatus.SUCCEEDED for s in pe.simulations]))
        self.validate_output(exp_id, 6)
        expected_tags = [{'a': '1', 'b': '2', 'c': '4'}, {'a': '1', 'b': '2', 'c': '5'}, {'a': '1', 'b': '3', 'c': '4'},
                         {'a': '1', 'b': '3', 'c': '5'}, {'a': '6', 'b': '2'}, {'a': '7', 'b': '2'}]
        self.validate_sim_tags(exp_id, expected_tags)

    @pytest.mark.comps
    def test_duplicate_asset_files_not_allowed(self):
        experiment = PythonExperiment(name=self.case_name,
                                      model_path=os.path.join(COMMON_INPUT_PATH, "python", "model1.py"))
        experiment.tags = {"idmtools": "idmtools-automation", "string_tag": "test", "number_tag": 123}
        experiment.assets.add_directory(
            assets_directory=os.path.join(COMMON_INPUT_PATH, "python", "folder_dup_file"))
        builder = ExperimentBuilder()
        experiment.builder = builder
        em = ExperimentManager(experiment=experiment, platform=self.platform)
        with self.assertRaises(RuntimeError) as context:
            em.run()
        self.assertTrue(
            "400 Bad Request - An error was encountered while attempting to save asset collection: Cannot insert "
            "duplicate key row in object 'dbo.AssetCollectionFile' with unique index "
            "'IX_AssetCollectionFile_AssetCollectionId_NewFileName_RelativePath_Unique'." in str(
                context.exception.args[0]))

    @pytest.mark.comps
    def test_use_existing_ac_with_experiment(self):
        model_path = os.path.join(COMMON_INPUT_PATH, "python", "model.py")
        platform = Platform('COMPS2')

        pe = PythonExperiment(name=self.case_name, model_path=model_path)
        pe.tags = {"idmtools": "idmtools-automation", "a": "1", "b": 2}

        # Get an existing asset collection (first create it for the test)
        assets_path = os.path.join(COMMON_INPUT_PATH, "python", "Assets")
        ac = AssetCollection.from_directory(assets_directory=assets_path)
        ids = self.platform.create_items([ac])
        comps_ac_id = ids[0]

        # Then get an "existing asset" to use for the experiment
        ac: AssetCollection = platform.get_item(comps_ac_id, item_type=ItemType.ASSETCOLLECTION, raw=False)
        self.assertIsInstance(ac, AssetCollection)
        pe.add_assets(ac)
        for asset in ac:
            self.assertIn(asset, pe.assets)

        pe.base_simulation.envelope = "parameters"
        pe.base_simulation.set_parameter("a", 1)
        pe.base_simulation.set_parameter("b", 10)

        sim = pe.simulation()
        builder = StandAloneSimulationsBuilder()
        builder.add_simulation(sim)
        pe.builder = builder

        em = ExperimentManager(experiment=pe, platform=platform)
        em.run()
        em.wait_till_done()
        self.assertTrue(all([s.status == EntityStatus.SUCCEEDED for s in pe.simulations]))
        exp_id = em.experiment.uid
        # validate results from comps
        for simulation in Experiment.get(exp_id).get_simulations():
            # validate output/config.json
            assets = self.assert_valid_config_stdout_and_assets(simulation)
            self.assertEqual(len(assets), 5)

            expected_list = [{'filename': '__init__.py', 'relative_path': 'MyExternalLibrary'},
                             {'filename': '__init__.py', 'relative_path': ''},
                             {'filename': 'model.py', 'relative_path': ''},
                             {'filename': 'temp.py', 'relative_path': 'MyLib'},
                             {'filename': 'functions.py', 'relative_path': 'MyExternalLibrary'}]
            self.validate_assets(assets, expected_list)

    @pytest.mark.comps
    def test_use_existing_ac_and_add_file_with_experiment(self):
        model_path = os.path.join(COMMON_INPUT_PATH, "compsplatform", "working_model.py")
        platform = Platform('COMPS2')
        pe = PythonExperiment(name=self.case_name, model_path=model_path)
        pe.tags = {"idmtools": "idmtools-automation", "string_tag": "existing ac and create new ac", "number_tag": 123}
        pe.base_simulation.envelope = "parameters"

        # Get an existing asset collection (first create it for the test)
        assets_path = os.path.join(COMMON_INPUT_PATH, "python", "Assets")
        ac = AssetCollection.from_directory(assets_directory=assets_path)
        ids = self.platform.create_items([ac])
        comps_ac_id = ids[0]

        # Then get an "existing asset" to use for the experiment
        ac: AssetCollection = platform.get_item(comps_ac_id, item_type=ItemType.ASSETCOLLECTION, raw=False)
        self.assertIsInstance(ac, AssetCollection)

        # Create new ac starting from an existing asset collection and add a file you need to run your experiment
        new_ac = AssetCollection(assets=ac.assets)
        new_ac.add_asset(Asset(relative_path=None, filename="test.json", content=json.dumps({"min_x": -2, "max_x": 2})))
        ids = self.platform.create_items([new_ac])
        new_ac = self.platform.get_item(ids[0], item_type=ItemType.ASSETCOLLECTION)
        self.assertIsInstance(new_ac, AssetCollection)
        pe.add_assets(copy.deepcopy(new_ac.assets))
        for asset in new_ac:
            self.assertIn(asset, pe.assets)

        builder = ExperimentBuilder()
        builder.add_sweep_definition(setParam("min_x"), range(-2, 1))
        builder.add_sweep_definition(setParam("max_x"), range(-2, 2))
        pe.add_builder(builder)

        em = ExperimentManager(experiment=pe, platform=platform)
        em.run()
        em.wait_till_done()
        self.assertTrue(all([s.status == EntityStatus.SUCCEEDED for s in pe.simulations]))
        exp_id = em.experiment.uid
        # validate results from comps
        for simulation in Experiment.get(exp_id).get_simulations():
            # validate output/config.json
            assets = self.assert_valid_new_assets(simulation)
            self.assertEqual(len(assets), 6)

            expected_list = [{'filename': '__init__.py', 'relative_path': 'MyExternalLibrary'},
                             {'filename': '__init__.py', 'relative_path': ''},
                             {'filename': 'temp.py', 'relative_path': 'MyLib'},
                             {'filename': 'functions.py', 'relative_path': 'MyExternalLibrary'},
                             {'filename': 'working_model.py', 'relative_path': ''},
                             {'filename': 'test.json', 'relative_path': ''}]
            self.validate_assets(assets, expected_list)

    def validate_output(self, exp_id, expected_sim_count):
        sim_count = 0
        for simulation in Experiment.get(exp_id).get_simulations():
            sim_count = sim_count + 1
            result_file_string = simulation.retrieve_output_files(paths=['output/result.json'])
            print(result_file_string)
            config_string = simulation.retrieve_output_files(paths=['config.json'])
            print(config_string)
            self.assertEqual(result_file_string, config_string)

        self.assertEqual(sim_count, expected_sim_count)

    def validate_sim_tags(self, exp_id, expected_tags):
        tags = []
        for simulation in Experiment.get(exp_id).get_simulations():
            tags.append(simulation.get(simulation.id, QueryCriteria().select_children('tags')).tags)

        sorted_tags = sorted(tags, key=itemgetter('a'))
        sorted_expected_tags = sorted(expected_tags, key=itemgetter('a'))
        self.assertEqual(sorted_tags, sorted_expected_tags)

    def validate_assets(self, assets, expected_list):
        actual_list = []
        for asset_collection_file in assets:
            file_relative_path_dict = dict()
            file_relative_path_dict['filename'] = asset_collection_file.file_name
            file_relative_path_dict['relative_path'] = asset_collection_file.relative_path or ""
            actual_list.append(file_relative_path_dict)
        expected_list_sorted = sorted(expected_list, key=itemgetter('filename', 'relative_path'))
        actual_list_sorted = sorted(actual_list, key=itemgetter('filename', 'relative_path'))
        self.assertEqual(expected_list_sorted, actual_list_sorted)


if __name__ == '__main__':
    unittest.main()
