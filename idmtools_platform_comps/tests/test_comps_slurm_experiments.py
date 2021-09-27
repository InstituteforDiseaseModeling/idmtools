import allure
import json
import os
from functools import partial
from typing import Any, Dict
import pytest
from COMPS.Data import Experiment as COMPSExperiment
from COMPS.Data import QueryCriteria
from idmtools import __version__
from idmtools.assets import AssetCollection
from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_platform_comps.utils.python_requirements_ac.requirements_to_asset_collection import \
    RequirementsToAssetCollection
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.common_experiments import wait_on_experiment_and_check_all_sim_status
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools_test.utils.shared_functions import validate_sim_tags, validate_output
from idmtools_test.utils.utils import get_case_name

setA = partial(JSONConfiguredPythonTask.set_parameter_sweep_callback, param="a")
setB = partial(JSONConfiguredPythonTask.set_parameter_sweep_callback, param="b")
setC = partial(JSONConfiguredPythonTask.set_parameter_sweep_callback, param="c")


class setParam:
    def __init__(self, param: str):
        self.param = param

    def __call__(self, simulation: Simulation, value) -> Dict[str, any]:
        return JSONConfiguredPythonTask.set_parameter_sweep_callback(simulation, self.param, value)


@pytest.mark.comps
@pytest.mark.python
@allure.story("COMPS")
@allure.story("Python")
@allure.story("COMPS-Slurm")
@allure.suite("idmtools_platform_comps")
class TestCOMPSSlurmExperiment(ITestWithPersistence):
    def setUp(self) -> None:
        self.case_name = get_case_name(os.path.basename(__file__) + "--" + self._testMethodName)
        print(self.case_name)
        self.platform = Platform('SLURM2')

    @pytest.mark.long
    @allure.story("Sweeps")
    def test_sweeps_with_partial_comps_in_slurm(self):
        model_path = os.path.join(COMMON_INPUT_PATH, "python", "model1.py")
        e = Experiment(name=self.case_name,
                       simulations=TemplatedSimulations(
                           base_task=JSONConfiguredPythonTask(python_path="python3", script_path=model_path)
                       ))
        e.tags = {"string_tag": "test", "number_tag": 123, "KeyOnly": None}
        builder = SimulationBuilder()
        # ------------------------------------------------------
        # Sweeping parameters:
        # first way to sweep parameter 'a' is to use param_update function
        builder.add_sweep_definition(setA, range(0, 2))

        # second way to sweep parameter 'b' is to use class setParam which basiclly doing same thing as param_update
        # method
        builder.add_sweep_definition(setParam("b"), [i * i for i in range(1, 4, 2)])
        # ------------------------------------------------------

        e.simulations.add_builder(builder)

        wait_on_experiment_and_check_all_sim_status(self, e, self.platform)
        experiment = COMPSExperiment.get(e.uid)
        print(experiment.id)
        exp_id = experiment.id
        # exp_id = "a727e802-d88b-e911-a2bb-f0921c167866"

        # validation each simulation output to compare output/config.json is equal to config.json
        validate_output(self, exp_id, 4)

        expected_tags = [{'a': '0', 'b': '1'}, {'a': '0', 'b': '9'}, {'a': '1', 'b': '1'}, {'a': '1', 'b': '9'}]
        task_type = 'idmtools_models.python.json_python_task.JSONConfiguredPythonTask'
        validate_sim_tags(self, exp_id, expected_tags, task_type)

        # validate experiment tags
        actual_exp_tags = experiment.get(experiment.id, QueryCriteria().select_children('tags')).tags
        expected_exp_tags = {'idmtools': __version__, 'number_tag': '123', 'string_tag': 'test',
                             'KeyOnly': '',
                             'task_type': task_type}
        self.assertDictEqual(expected_exp_tags, actual_exp_tags)
        self.assertDictEqual(expected_exp_tags, actual_exp_tags)

    @pytest.mark.skip(reason='test still fail with error we can not control')
    @pytest.mark.long
    @pytest.mark.comps
    def test_seir_model_experiment_slurm(self):
        # ye_seir_model assets path
        assets_path = os.path.join(COMMON_INPUT_PATH, "python", "ye_seir_model", "Assets")

        pl = RequirementsToAssetCollection(name=self.case_name, platform=self.platform, requirements_path=os.path.join(assets_path, 'requirements.txt'))

        ac_id = pl.run(rerun=False)
        pandas_assets = AssetCollection.from_id(ac_id, platform=self.platform, as_copy=True)

        # Define some constant string used in this example
        class ConfigParameters:
            Infectious_Period_Constant = "Infectious_Period_Constant"
            Base_Infectivity_Constant = "Base_Infectivity_Constant"
            Base_Infectivity_Distribution = "Base_Infectivity_Distribution"
            GAUSSIAN_DISTRIBUTION = "GAUSSIAN_DISTRIBUTION"
            Base_Infectivity_Gaussian_Mean = "Base_Infectivity_Gaussian_Mean"
            Base_Infectivity_Gaussian_Std_Dev = "Base_Infectivity_Gaussian_Std_Dev"

        # ------------------------------------------------------
        # First run the experiment
        # ------------------------------------------------------
        # script_path = os.path.join(COMMON_INPUT_PATH, "python", "ye_seir_model", "Assets", "SEIR_model.py")
        tags = {"idmtools": "idmtools-automation", "simulation_name_tag": "SEIR_Model_SLURM"}

        parameters = json.load(
            open(os.path.join(assets_path, "templates", 'config.json'),
                 'r'))
        parameters[ConfigParameters.Base_Infectivity_Distribution] = ConfigParameters.GAUSSIAN_DISTRIBUTION
        # Pass python_path as python3 for SLURM cluster (python2 is currently the default)
        python_path_script = os.path.join(assets_path, "SEIR_model_slurm.py")
        task = JSONConfiguredPythonTask(script_path=python_path_script, parameters=parameters,
                                        config_file_name='config.json', common_assets=pandas_assets)
        task.command.add_option("--duration", 40)

        # now create a TemplatedSimulation builder
        ts = TemplatedSimulations(base_task=task)
        ts.base_simulation.tags['simulation_name_tag'] = "SEIR_Model"

        # now define our sweeps
        builder = SimulationBuilder()

        # utility function to update parameters
        def param_update(simulation: Simulation, param: str, value: Any) -> Dict[str, Any]:
            return simulation.task.set_parameter(param, value)

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
        experiment.run()

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
