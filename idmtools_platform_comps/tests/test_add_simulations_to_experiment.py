import allure
import os

import pytest
from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools_test.utils.utils import get_case_name


@pytest.mark.comps
@allure.story("COMPS")
@allure.story("Modify Experiments")
@allure.suite("idmtools_platform_comps")
class TestAddSimulationsToExperiment(ITestWithPersistence):

    def setUp(self) -> None:
        self.case_name = get_case_name(os.path.basename(__file__) + "--" + self._testMethodName)
        self.platform = Platform('Bayesian')

    # test add TemlatedSimulations to existing experiment with extend
    @pytest.mark.smoke
    def test_add_simulations_to_existing_experiment(self):
        # First create experiment with single simulation via JSONConfiguredPythonTask
        config = {"a": 1, "b": 2}
        experiment = self.get_working_model_experiment(config)
        experiment.run(wait_until_done=True)
        self.assertTrue(experiment.succeeded)
        self.assertEqual(1, len(experiment.simulations))
        files_needed = ["Assets/working_model.py"]
        self.verify_assets(experiment, files_needed)

        # add new simulations to above experiment
        # first copy experiment assets to new AssetCollection object
        experiment.assets = experiment.assets.copy()
        model_path = os.path.join(COMMON_INPUT_PATH, "python", "hello_world.py")
        sims_template = self.get_templatedsimluation(model_path, n=3)
        experiment.simulations.extend(sims_template)
        experiment.run(wait_until_done=True, regather_common_assets=True)
        self.assertTrue(experiment.succeeded)
        self.assertEqual(3, len(experiment.simulations))
        files_needed = ["Assets/working_model.py", "Assets/hello_world.py"]
        self.verify_assets(experiment, files_needed)

    # test add single simulation to existing experiment with append
    def test_add_simulations_to_existing_experiment_1(self):
        # Create experiment with 1 simulation via CommandTask
        command = "python -m pip list"
        task = CommandTask(command=command)
        experiment = Experiment.from_task(task, name=self.case_name)
        experiment.run(wait_until_done=True)
        self.assertEqual(1, len(experiment.simulations))
        files_needed = ["StdErr.txt", "StdOut.txt"]
        self.verify_assets(experiment, files_needed)
        # add another sim to the experiment
        sim = task.to_simulation()
        experiment.simulations.append(sim)
        experiment.run(wait_until_done=True)

        self.assertTrue(experiment.succeeded)
        self.assertEqual(2, len(experiment.simulations))
        files_needed = ["StdErr.txt", "StdOut.txt"]
        self.verify_assets(experiment, files_needed)

    # test add 2 simulations to existing experiment with extend
    def test_add_simulations_to_existing_experiment_2(self):
        # create experiment with 1 Simulation from JSONConfiguredPythonTask
        experiment = self.get_working_model_experiment()
        experiment.run(wait_until_done=True)
        self.assertEqual(1, len(experiment.simulations))
        files_needed = ["Assets/working_model.py"]
        self.verify_assets(experiment, files_needed)
        # need to copy experiment assets(origin experiment assets is not editable
        experiment.assets = experiment.assets.copy()
        # add another 2 sims with JSONConfiguredPythonTask to the experiment
        model_path = os.path.join(COMMON_INPUT_PATH, "python", "newmodel2.py")
        task = JSONConfiguredPythonTask(script_path=model_path, parameters=dict(a=1))

        sims = [task.to_simulation(), task.to_simulation()]
        experiment.simulations.extend(sims)
        experiment.run(wait_until_done=True, regather_common_assets=True)
        self.assertTrue(experiment.succeeded)
        self.assertEqual(3, len(experiment.simulations))
        files_needed = ["Assets/working_model.py", "Assets/newmodel2.py"]
        self.verify_assets(experiment, files_needed)

    # test add TemplatedSimulations to existing experiment with extend
    def test_add_simulations_to_existing_experiment_3(self):
        # create experiment with TemplatedSimulation
        model_path = os.path.join(COMMON_INPUT_PATH, "python", "newmodel2.py")
        sims_template = self.get_templatedsimluation(model_path)
        experiment = Experiment.from_template(sims_template, name=self.case_name)
        experiment.run(wait_until_done=True)
        self.assertEqual(4, len(experiment.simulations))
        files_needed = ["Assets/newmodel2.py"]
        self.verify_assets(experiment, files_needed)
        # add same assets(script) with new TemplatedSimulations to exsiting experiment,
        # note, no need to copy experiment assets here
        sims_template = self.get_templatedsimluation(model_path)
        experiment.simulations.extend(sims_template)
        experiment.run(wait_until_done=True)
        self.assertTrue(experiment.succeeded)
        self.assertEqual(8, len(experiment.simulations))
        files_needed = ["Assets/newmodel2.py"]
        self.verify_assets(experiment, files_needed)

    # test add extra single simulation to newly created but not commissioned experiment with append
    def test_add_more_simulations_to_new_experiment_1(self):
        # add one single Simulation via CommandTask
        command = "python -m pip list"
        task = CommandTask(command=command)
        experiment = Experiment.from_task(task, name=self.case_name)
        # add another sim to the experiment
        sim = task.to_simulation()
        experiment.simulations.append(sim)
        experiment.run(wait_until_done=True)

        self.assertTrue(experiment.succeeded)
        self.assertEqual(2, len(experiment.simulations))

        files_needed = ["StdErr.txt", "StdOut.txt"]
        self.verify_assets(experiment, files_needed)

    # test add extra simulations to newly created but not commissioned experiment with extend
    def test_add_more_simulations_to_new_experiment_2(self):
        # create experiment with 1 Simulation from JSONConfiguredPythonTask
        experiment = self.get_working_model_experiment()

        # add another 2 sims with JSONConfiguredPythonTask to the experiment
        model_path = os.path.join(COMMON_INPUT_PATH, "python", "newmodel2.py")
        task = JSONConfiguredPythonTask(script_path=model_path, parameters=dict(a=1))
        sims = [task.to_simulation(), task.to_simulation()]
        # add sims to experiment
        experiment.simulations.extend(sims)
        experiment.run(wait_until_done=True)

        self.assertTrue(experiment.succeeded)
        self.assertEqual(3, len(experiment.simulations))

        # make sure Assets files are correct
        files_needed = ["Assets/working_model.py", "Assets/newmodel2.py"]
        self.verify_assets(experiment, files_needed)

    # test add TemplatedSimulations to newly created but not commissioned experiment with extend
    def test_add_more_simulations_to_new_experiment_3(self):
        # create experiment with 1 Simulation via JSONConfiguredPythonTask
        experiment = self.get_working_model_experiment()
        # add  TemplatedSimulations to the experiment
        model_path = os.path.join(COMMON_INPUT_PATH, "python", "hello_world.py")
        sims_template = self.get_templatedsimluation(model_path)
        experiment.simulations.extend(sims_template)
        experiment.run(wait_until_done=True)

        self.assertTrue(experiment.succeeded)
        self.assertEqual(5, len(experiment.simulations))

        # make sure Assets files are correct
        files_needed = ["Assets/working_model.py", "Assets/hello_world.py"]
        self.verify_assets(experiment, files_needed)

    def test_add_more_simulations_to_new_experiment_4(self):
        # create 1 TemplatedSimulations
        model_path = os.path.join(COMMON_INPUT_PATH, "python", "newmodel2.py")
        sims_template = self.get_templatedsimluation(model_path)
        experiment = Experiment.from_template(sims_template, name=self.case_name)
        # add templatedsimulation with same asset
        sims_template = self.get_templatedsimluation(model_path)
        # Add second templatedsumulation to the experiment
        experiment.simulations.extend(sims_template)
        experiment.run(wait_until_done=True)

        self.assertTrue(experiment.succeeded)
        self.assertEqual(8, len(experiment.simulations))
        # make sure Assets files are correct
        files_needed = ["Assets/newmodel2.py"]
        self.verify_assets(experiment, files_needed)

    def get_working_model_experiment(self, config=None, script="working_model.py") -> Experiment:
        if config is None:
            config = dict()
        model_path = os.path.join(COMMON_INPUT_PATH, "compsplatform", script)
        task = JSONConfiguredPythonTask(script_path=model_path, parameters=config)
        experiment = Experiment.from_task(task, name=self.case_name)
        return experiment

    def get_templatedsimluation(self, model_path, n=5):
        builder = SimulationBuilder()
        builder.add_sweep_definition(JSONConfiguredPythonTask.set_parameter_partial("a"),
                                     [i * i for i in range(1, n)])
        sims_template = TemplatedSimulations(
            base_task=JSONConfiguredPythonTask(script_path=model_path, parameters=dict(a=100)))
        sims_template.add_builder(builder=builder)
        return sims_template

    def verify_assets(self, experiment, files_needed):
        files_retrieved = self.platform.get_files(item=experiment.simulations[0], files=files_needed)
        # We have the correct files?
        self.assertEqual(len(files_needed), len(files_retrieved))
