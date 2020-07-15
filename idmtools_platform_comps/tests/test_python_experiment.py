import copy
import json
import os
import unittest
from functools import partial
from operator import itemgetter
from typing import Any, Dict

import pytest
from COMPS.Data import Experiment as COMPSExperiment, AssetCollection as COMPSAssetCollection
from COMPS.Data import QueryCriteria
from idmtools import __version__
from idmtools.assets import Asset, AssetCollection
from idmtools.builders import ArmSimulationBuilder, ArmType, SimulationBuilder, SweepArm
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.common_experiments import get_model1_templated_experiment, get_model_py_templated_experiment, \
    wait_on_experiment_and_check_all_sim_status
from idmtools_test.utils.comps import get_asset_collection_id_for_simulation_id, get_asset_collection_by_id
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools_test.utils.shared_functions import validate_output, validate_sim_tags

setA = partial(JSONConfiguredPythonTask.set_parameter_sweep_callback, param="a")
setB = partial(JSONConfiguredPythonTask.set_parameter_sweep_callback, param="b")
setC = partial(JSONConfiguredPythonTask.set_parameter_sweep_callback, param="c")


class setParam:
    def __init__(self, param: str):
        self.param = param

    def __call__(self, simulation: Simulation, value) -> Dict[str, any]:
        # set simulation name
        simulation.name = f'{simulation.parent.name}_{self.param}_{value}'
        return JSONConfiguredPythonTask.set_parameter_sweep_callback(simulation, self.param, value)


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
    def test_sweeps_with_partial_comps(self):   # zdu: no metadata file any more

        e = get_model1_templated_experiment(self.case_name)
        builder = SimulationBuilder()
        # ------------------------------------------------------
        # Sweeping parameters:
        # first way to sweep parameter 'a' is to use param_update function
        builder.add_sweep_definition(
            JSONConfiguredPythonTask.set_parameter_partial("a"),
            range(0, 2)
        )

        # second way to sweep parameter 'b' is to use class setParam which basiclly doing same thing as param_update
        # method
        builder.add_sweep_definition(
            JSONConfiguredPythonTask.set_parameter_partial("b"),
            [i * i for i in range(1, 4, 2)]
        )
        # ------------------------------------------------------

        e.simulations.add_builder(builder)

        wait_on_experiment_and_check_all_sim_status(self, e, self.platform)
        experiment = COMPSExperiment.get(e.uid)
        print(experiment.id)
        exp_id = experiment.id
        # exp_id = "a727e802-d88b-e911-a2bb-f0921c167866"

        # validation each simulation output to compare output/config.json is equal to config.json
        validate_output(self, exp_id, 4)
        tag_value = "idmtools_models.python.json_python_task.JSONConfiguredPythonTask"
        expected_tags = [{'a': '0', 'b': '1', 'task_type': tag_value}, {'a': '0', 'b': '9', 'task_type': tag_value},
                         {'a': '1', 'b': '1', 'task_type': tag_value}, {'a': '1', 'b': '9', 'task_type': tag_value}]
        validate_sim_tags(self, exp_id, expected_tags, tag_value)

        # validate experiment tags
        actual_exp_tags = experiment.get(experiment.id, QueryCriteria().select_children('tags')).tags
        expected_exp_tags = {'idmtools': __version__, 'number_tag': '123', 'string_tag': 'test',
                             'KeyOnly': '',
                             'task_type': 'idmtools_models.python.json_python_task.JSONConfiguredPythonTask'}
        self.assertDictEqual(expected_exp_tags, actual_exp_tags)
        self.assertDictEqual(expected_exp_tags, actual_exp_tags)

        # validate reload
        # with self.subTest("test_sweeps_with_partial_comps_reload_with_task"):
        #     experiment_reload = Experiment.from_id(e.uid, self.platform, load_task=True)
        #     self.assertEqual(e.id, experiment_reload.id)
        #     self.assertEqual(e.simulation_count, experiment_reload.simulation_count)
        #     # get all the ids
        #     self.assertEqual(
        #         sorted([s.uid for s in e.simulations]),
        #         sorted([s.uid for s in experiment_reload.simulations])
        #     )
        #     for sim in experiment_reload.simulations:
        #         self.assertIsInstance(sim.task, JSONConfiguredPythonTask)
        #         self.assertIn("a", sim.task.parameters)
        #         self.assertIn("b", sim.task.parameters)
        #         self.assertEqual(str(e.simulations[0].task.command), str(sim.task.command))

        with self.subTest("test_sweeps_with_partial_comps_reload"):
            experiment_reload = Experiment.from_id(e.uid, self.platform)
            for sim in experiment_reload.simulations:
                self.assertIsInstance(sim.task, CommandTask)
                'python ./Assets/model1.py --config config.json'
                self.assertEqual(str(e.simulations[0].task.command), str(sim.task.command))

    # Test parameter "b" set is depending on parameter "a"
    # a=[0,1,2,3,4] <--sweep parameter
    # b=[2,3,4,5,6]  <-- b = a + 2
    @pytest.mark.long
    def test_sweeps_2_related_parameters_comps(self):
        e = get_model1_templated_experiment(self.case_name)

        def param_update_ab(simulation: Simulation, param: str, value: Any) -> Dict[str, any]:
            # Set B within
            if param == "a":
                simulation.task.set_parameter("b", value + 2)

            return simulation.task.set_parameter(param, value)

        setAB = partial(param_update_ab, param="a")

        builder = SimulationBuilder()
        # Sweep parameter "a" and make "b" depends on "a"
        builder.add_sweep_definition(setAB, range(0, 5))
        e.simulations.add_builder(builder)

        wait_on_experiment_and_check_all_sim_status(self, e, self.platform)

        experiment = COMPSExperiment.get(e.uid)
        print(experiment.id)
        exp_id = experiment.id
        validate_output(self, exp_id, 5)

        # validate b is not in tag since it is not sweep parameter, it just depend on sweep parameter
        tag_value = "idmtools_models.python.json_python_task.JSONConfiguredPythonTask"
        expected_tags = [{'a': '0', 'task_type': tag_value}, {'a': '1', 'task_type': tag_value},
                         {'a': '2', 'task_type': tag_value}, {'a': '3', 'task_type': tag_value},
                         {'a': '4', 'task_type': tag_value}]
        validate_sim_tags(self, exp_id, expected_tags, tag_value)

    @pytest.mark.long
    @pytest.mark.comps
    def test_add_prefixed_relative_path_to_assets_comps(self):
        e = get_model_py_templated_experiment(self.case_name, dict(b=10))

        def param_a_update(simulation: Simulation, value) -> Dict[str, Any]:
            simulation.task.set_parameter("a", value)
            return {"a": value}

        builder = SimulationBuilder()
        # Sweep parameter "a"
        builder.add_sweep_definition(param_a_update, range(0, 2))
        e.simulations.add_builder(builder)

        wait_on_experiment_and_check_all_sim_status(self, e, self.platform)

        exp_id = e.uid
        # exp_id ='ef8e7f2f-a793-e911-a2bb-f0921c167866'
        count = 0
        for simulation in COMPSExperiment.get(exp_id).get_simulations():
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
    # COMPS' Assets folder
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
        e = get_model_py_templated_experiment(self.case_name,
                                              assets_path=os.path.join(COMMON_INPUT_PATH, "python", "Assets"),
                                              relative_path=None)
        # sim = pe.simulation() # uncomment this line when issue #138 gets fixed
        # TODO update this syntax in TC. We have better manual building methods for simulations
        sim = e.simulations.new_simulation()
        sim.task.set_parameter("a", 1)
        sim.task.set_parameter("b", 10)

        e.simulations = [sim]

        wait_on_experiment_and_check_all_sim_status(self, e, self.platform)

        exp_id = e.uid
        self.validate_model_py_relative_assets(exp_id)

    def validate_model_py_relative_assets(self, exp_id, validate_config=True, validate_stdout=True):
        # validate results from comps
        # exp_id ='eb7ce224-9993-e911-a2bb-f0921c167866'
        for simulation in COMPSExperiment.get(exp_id).get_simulations():
            # validate output/config.json
            assets = self.assert_valid_config_stdout_and_assets(simulation, validate_config=validate_config,
                                                                validate_stdout=validate_stdout)
            self.assertEqual(len(assets), 5)

            expected_list = [{'filename': '__init__.py', 'relative_path': 'MyExternalLibrary'},
                             {'filename': '__init__.py', 'relative_path': ''},
                             {'filename': 'model.py', 'relative_path': ''},
                             {'filename': 'temp.py', 'relative_path': 'MyLib'},
                             {'filename': 'functions.py', 'relative_path': 'MyExternalLibrary'}]
            self.validate_assets(assets, expected_list)

    def assert_valid_config_stdout_and_assets(self, simulation, validate_config=True, validate_stdout=True):
        if validate_config:
            config_string = simulation.retrieve_output_files(paths=["config.json"])
            config_parameters = json.loads(config_string[0].decode('utf-8'))['parameters']
            self.assertEqual(config_parameters["a"], 1)
            self.assertEqual(config_parameters["b"], 10)
        if validate_stdout:
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

        base_task = JSONConfiguredPythonTask(parameters=dict(a=1, b=10), envelope="parameters", script_path=model_path)
        e = Experiment(name=self.case_name, assets=ac, simulations=[base_task.to_simulation()],
                       gather_common_assets_from_task=True)
        e.tags = {"string_tag": "test", "number_tag": 123}

        wait_on_experiment_and_check_all_sim_status(self, e, self.platform)

        exp_id = e.uid
        # validate results from comps
        # exp_id ='a98090dc-ea92-e911-a2bb-f0921c167866'
        for simulation in COMPSExperiment.get(exp_id).get_simulations():
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

        base_task = JSONConfiguredPythonTask(script_path=os.path.join(COMMON_INPUT_PATH, "python", "model1.py"))
        ts = TemplatedSimulations(base_task=base_task)

        # create our ARM builder
        builder = ArmSimulationBuilder()
        # create sweeep cross
        arm = SweepArm(type=ArmType.cross)
        arm.add_sweep_definition(setA, 1)
        arm.add_sweep_definition(setB, [2, 3])
        arm.add_sweep_definition(setC, [4, 5])
        builder.add_arm(arm)

        # add another cross arm
        arm = SweepArm(type=ArmType.cross)
        arm.add_sweep_definition(setA, [6, 7])
        arm.add_sweep_definition(setB, [2])
        builder.add_arm(arm)
        # Add the builder to our templated sim
        ts.add_builder(builder)

        e = Experiment(name=self.case_name, simulations=ts)
        tags = {
            "string_tag": "test", "number_tag": 123, "KeyOnly": None
        }
        e.tags = tags

        wait_on_experiment_and_check_all_sim_status(self, e, self.platform)
        exp_id = e.uid
        validate_output(self, exp_id, 6)
        tag_value = "idmtools_models.python.json_python_task.JSONConfiguredPythonTask"
        expected_tags = [{'a': '1', 'b': '2', 'c': '4', 'task_type': tag_value},
                         {'a': '1', 'b': '2', 'c': '5', 'task_type': tag_value},
                         {'a': '1', 'b': '3', 'c': '4', 'task_type': tag_value},
                         {'a': '1', 'b': '3', 'c': '5', 'task_type': tag_value},
                         {'a': '6', 'b': '2', 'task_type': tag_value},
                         {'a': '7', 'b': '2', 'task_type': tag_value}]
        validate_sim_tags(self, exp_id, expected_tags, tag_value)

    @pytest.mark.comps
    def test_duplicate_asset_files_not_allowed(self):
        script_path = os.path.join(COMMON_INPUT_PATH, "python", "model1.py")
        experiment = Experiment(name=self.case_name,
                                simulations=[JSONConfiguredPythonTask(script_path=script_path)],
                                tags={"string_tag": "test", "number_tag": 123}, gather_common_assets_from_task=True)
        experiment.assets.add_directory(
            assets_directory=os.path.join(COMMON_INPUT_PATH, "python", "folder_dup_file"))
        with self.assertRaises(RuntimeError) as context:
            self.platform.run_items(experiment)
        self.assertTrue(
            "400 Bad Request - An error was encountered while attempting to save asset collection: Cannot insert "
            "duplicate key row in object 'dbo.AssetCollectionFile' with unique index "
            "'IX_AssetCollectionFile_AssetCollectionId_NewFileName_RelativePath_Unique'." in str(
                context.exception.args[0]))

    @pytest.mark.comps
    @pytest.mark.long
    def test_use_existing_ac_with_experiment(self):
        model_path = os.path.join(COMMON_INPUT_PATH, "python", "model.py")
        tags = {"a": "1", "b": 10}
        t = JSONConfiguredPythonTask(script_path=model_path, parameters=dict(a=1, b=10), envelope="parameters")
        ts = TemplatedSimulations(base_task=t)
        ts.tags = tags
        e = Experiment(name=self.case_name, simulations=[ts.new_simulation()], gather_common_assets_from_task=True)

        ac = self.get_existing_python_asset_collection()
        e.add_assets(ac)
        for asset in ac:
            self.assertIn(asset, e.assets)

        wait_on_experiment_and_check_all_sim_status(self, e, self.platform)
        exp_id = e.uid
        # validate results from comps
        self.validate_model_py_relative_assets(exp_id)

    def get_existing_python_asset_collection(self):
        # Get an existing asset collection (first create it for the test)
        assets_path = os.path.join(COMMON_INPUT_PATH, "python", "Assets")
        ac = AssetCollection.from_directory(assets_directory=assets_path)
        items = self.platform.create_items([ac])
        self.assertEqual(len(items), 1)
        # TODO fix return of create
        self.assertIsInstance(items[0], COMPSAssetCollection)
        comps_ac_id = ac.uid
        # Then get an "existing asset" to use for the experiment
        ac: AssetCollection = self.platform.get_item(comps_ac_id, item_type=ItemType.ASSETCOLLECTION, raw=False)
        self.assertIsInstance(ac, AssetCollection)
        return ac

    @pytest.mark.smoke
    @pytest.mark.comps
    def test_use_existing_ac_and_add_file_with_experiment(self):
        model_path = os.path.join(COMMON_INPUT_PATH, "compsplatform", "working_model.py")
        bt = JSONConfiguredPythonTask(script_path=model_path, envelope="parameters")
        ts = TemplatedSimulations(base_task=bt)

        builder = SimulationBuilder()
        builder.add_sweep_definition(setParam("min_x"), range(-2, 1))
        builder.add_sweep_definition(setParam("max_x"), range(-2, 2))
        ts.add_builder(builder)
        tags = {"string_tag": "existing ac and create new ac", "number_tag": 123}
        ts.tags = tags

        e = Experiment(name=self.case_name, simulations=ts)
        ac = self.get_existing_python_asset_collection()

        # Create new ac starting from an existing asset collection and add a file you need to run your experiment
        new_ac = AssetCollection(ac.assets)
        new_ac.add_asset(Asset(relative_path=None, filename="test.json", content=json.dumps({"min_x": -2, "max_x": 2})))
        self.platform.create_items([new_ac])
        new_ac = self.platform.get_item(new_ac.uid, item_type=ItemType.ASSETCOLLECTION)
        self.assertIsInstance(new_ac, AssetCollection)
        e.add_assets(copy.deepcopy(new_ac.assets))
        for asset in new_ac:
            self.assertIn(asset, e.assets)

        wait_on_experiment_and_check_all_sim_status(self, e, self.platform)
        exp_id = e.uid
        # don't validate stdout since we it isn't the typical out since we use different parameters
        for simulation in COMPSExperiment.get(exp_id).get_simulations():
            # validate output/config.json
            assets = self.assert_valid_new_assets(simulation)
            self.assertEqual(len(assets), 6)

            expected_list = [{'filename': '__init__.py', 'relative_path': 'MyExternalLibrary'},
                             {'filename': '__init__.py', 'relative_path': ''},
                             {'filename': 'temp.py', 'relative_path': 'MyLib'},
                             {'filename': 'functions.py', 'relative_path': 'MyExternalLibrary'},
                             {'filename': 'working_model.py', 'relative_path': ''},
                             {'filename': 'test.json', 'relative_path': ''}]
            # validate simulation names
            self.assertIn(f'{e.name}_', simulation.name)
            self.validate_assets(assets, expected_list)

    @pytest.mark.long
    @pytest.mark.comps
    def test_seir_model_experiment(self):
        # Define some constant string used in this example
        class ConfigParameters:
            Infectious_Period_Constant = "Infectious_Period_Constant"
            Base_Infectivity_Constant = "Base_Infectivity_Constant"
            Base_Infectivity_Distribution = "Base_Infectivity_Distribution"
            GAUSSIAN_DISTRIBUTION = "GAUSSIAN_DISTRIBUTION"
            Base_Infectivity_Gaussian_Mean = "Base_Infectivity_Gaussian_Mean"
            Base_Infectivity_Gaussian_Std_Dev = "Base_Infectivity_Gaussian_Std_Dev"

        # First run the experiment
        script_path = os.path.join(COMMON_INPUT_PATH, "python", "ye_seir_model", "Assets", "SEIR_model.py")
        assets_path = os.path.join(COMMON_INPUT_PATH, "python", "ye_seir_model", "Assets")
        tags = {"idmtools": "idmtools-automation", "simulation_name_tag": "SEIR_Model"}

        parameters = json.load(
            open(os.path.join(assets_path, "templates", 'config.json'),
                 'r'))
        parameters[ConfigParameters.Base_Infectivity_Distribution] = ConfigParameters.GAUSSIAN_DISTRIBUTION
        task = JSONConfiguredPythonTask(script_path=script_path, parameters=parameters,
                                        config_file_name='config.json')
        task.command.add_option("--duration", 40)

        # now create a TemplatedSimulation builder
        ts = TemplatedSimulations(base_task=task)
        ts.base_simulation.tags['simulation_name_tag'] = "SEIR_Model"

        # now define our sweeps
        builder = SimulationBuilder()

        # utility function to update parameters
        def param_update(simulation: Simulation, param: str, value: Any) -> Dict[str, Any]:
            return simulation.task.set_parameter(param, value)

        # set_base_infectivity_gaussian_mean = partial(param_update,
        #                                              param=ConfigParameters.Base_Infectivity_Gaussian_Mean)

        class setParam:
            def __init__(self, param):
                self.param = param

            def __call__(self, simulation, value):
                return simulation.task.set_parameter(self.param, value)

        builder.add_sweep_definition(setParam(ConfigParameters.Base_Infectivity_Gaussian_Std_Dev), [0.3, 1])

        ts.add_builder(builder)
        ts.tags = tags

        # now we can create our experiment using our template builder
        experiment = Experiment(name=self.case_name, simulations=ts)
        experiment.tags = tags

        experiment.assets.add_directory(assets_directory=assets_path)

        # set platform and run simulations
        self.platform.run_items(experiment)
        self.platform.wait_till_done(experiment)

        # check experiment status
        wait_on_experiment_and_check_all_sim_status(self, experiment, self.platform)

        # validate sim outputs
        exp_id = experiment.id
        self.validate_custom_output(exp_id, 2)

    def validate_custom_output(self, exp_id, expected_sim_count):
        sim_count = 0
        for simulation in COMPSExperiment.get(exp_id).get_simulations():
            sim_count = sim_count + 1
            expected_csv_output_1 = simulation.retrieve_output_files(paths=['output/individual.csv'])
            expected_csv_output_2 = simulation.retrieve_output_files(paths=['output/node.csv'])
            self.assertEqual(len(expected_csv_output_1), 1)
            self.assertEqual(len(expected_csv_output_2), 1)

        self.assertEqual(sim_count, expected_sim_count)

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
