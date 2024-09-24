import allure
import os
import sys
from unittest import TestCase
import pytest
from idmtools.builders import SimulationBuilder
from idmtools.core import EntityStatus
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_models.python.python_task import PythonTask
from idmtools_test import COMMON_INPUT_PATH


@pytest.mark.tasks
@pytest.mark.smoke
@allure.story("Python")
@allure.suite("idmtools_models")
class TestPythonTask(TestCase):

    @pytest.mark.smoke
    def test_simple_model(self):
        fpath = os.path.join(COMMON_INPUT_PATH, "python", "model1.py")
        task = PythonTask(script_path=fpath)
        task.gather_all_assets()
        task.pre_creation(None, Platform("Test"))

        self.assertEqual(str(task.command), f'python Assets/model1.py')
        self.validate_common_assets(fpath, task)

    def validate_common_assets(self, fpath, task):
        """
        Validate common assets on a python model

        Args:
            fpath: Source path to model file
            task: Task object to validate

        Returns:
            None
        """
        self.assertEqual(len(task.common_assets.assets), 1, f'Asset list is: {[str(x) for x in task.common_assets.assets]}')
        self.assertEqual(task.common_assets.assets[0].absolute_path, fpath)

    def validate_json_transient_assets(self, task, config_file_name='config.json'):
        """
        Validate JSON Python task has correct transient assets
        Args:
            task: Task to validate
            config_file_name: Files name the json config should be. Default to config.json
        Returns:

        """
        self.assertEqual(len(task.transient_assets.assets), 1)
        self.assertEqual(task.transient_assets.assets[0].filename, config_file_name)

    def test_json_python_argument(self):
        """
        Validates JSON Command on Python Task
        Returns:

        """
        fpath = os.path.join(COMMON_INPUT_PATH, "python", "model1.py")
        task = JSONConfiguredPythonTask(script_path=fpath)
        task.gather_all_assets()
        task.pre_creation(None, Platform("Test"))

        self.assertEqual(str(task.command), f'python Assets/model1.py --config config.json')
        self.validate_common_assets(fpath, task)
        self.validate_json_transient_assets(task)

    def test_json_python_static_filename_no_argument(self):
        """
        Test with No Config file argument
        Returns:

        """
        fpath = os.path.join(COMMON_INPUT_PATH, "python", "model1.py")
        # here we test a script that may have no config
        task = JSONConfiguredPythonTask(script_path=fpath, configfile_argument=None)
        task.gather_all_assets()
        task.pre_creation(None, Platform("Test"))

        self.assertEqual(str(task.command), f'python Assets/model1.py')
        self.validate_common_assets(fpath, task)
        self.validate_json_transient_assets(task)

    def test_different_python_path(self):
        """
        Test with different python path

        Returns:

        """
        fpath = os.path.join(COMMON_INPUT_PATH, "python", "model1.py")
        task = JSONConfiguredPythonTask(script_path=fpath, configfile_argument=None, python_path='python3.8')
        task.gather_all_assets()
        task.pre_creation(None, Platform("Test"))

        self.assertEqual(str(task.command), f'python3.8 Assets/model1.py')
        self.validate_common_assets(fpath, task)
        self.validate_json_transient_assets(task)

    @pytest.mark.serial
    def test_model1(self):
        """
        Test local execution of the model1 python script using JSONConfiguredPythonTask

        Also run a sub-test where we fetch the with the created simulation

        Returns:

        """
        with Platform("TestExecute", type='TestExecute'):
            fpath = os.path.join(COMMON_INPUT_PATH, "python", "model1.py")
            # here we test a script
            params = dict(a=1, b=2, c=3)
            task = JSONConfiguredPythonTask(
                script_path=fpath,
                configfile_argument=None,
                python_path=sys.executable,
                parameters=params
            )
            experiment = Experiment.from_task(task)
            experiment.run(True)

            self.assertTrue(experiment.succeeded)
            self.assertEqual(1, experiment.simulation_count)
            self.assertEqual(EntityStatus.SUCCEEDED, experiment.simulations[0].status)

            # WE Need to verify more output here

            with self.subTest("test_model1_reload_simulation_task"):
                experiment_reload = Experiment.from_id(experiment.uid, load_task=True)
                self.assertEqual(experiment.id, experiment_reload.id)
                self.assertEqual(experiment.simulation_count, experiment_reload.simulation_count)
                self.assertEqual(experiment.succeeded, experiment_reload.succeeded)
                sim1: Simulation = experiment_reload.simulations[0]
                self.assertEqual(experiment.simulations[0].uid, sim1.uid)
                self.assertEqual(0, sim1.assets.count)
                self.assertEqual(experiment.simulations[0].task.command, sim1.task.command)
                self.assertEqual(params, sim1.task.parameters)

            with self.subTest("test_model1_reload_simulation"):
                experiment_reload = Experiment.from_id(experiment.uid)
                self.assertEqual(experiment.id, experiment_reload.id)
                self.assertEqual(experiment.simulation_count, experiment_reload.simulation_count)
                self.assertEqual(experiment.succeeded, experiment_reload.succeeded)
                sim1: Simulation = experiment_reload.simulations[0]
                self.assertEqual(experiment.simulations[0].uid, sim1.uid)
                self.assertEqual(1, sim1.assets.count)
                self.assertEqual(experiment.simulations[0].task.command, sim1.task.command)

    @pytest.mark.serial
    def test_model_sweep(self):
        """
        Test model Sweep using JSONConfiguredPythonTask

        In addition test model reload with deep task reload and without
        Returns:

        """
        with Platform("TestExecute", type='TestExecute'):
            fpath = os.path.join(COMMON_INPUT_PATH, "python", "model1.py")
            # here we test a script that may have no config
            task = JSONConfiguredPythonTask(script_path=fpath, configfile_argument=None, python_path=sys.executable)
            builder = SimulationBuilder()
            builder.add_sweep_definition(task.set_parameter_partial("a"), range(2))
            builder.add_sweep_definition(task.set_parameter_partial("b"), range(2))
            experiment = Experiment.from_builder(builder, base_task=task)
            experiment.run(True)

            self.assertEqual(True, experiment.succeeded)
            self.assertEqual(4, experiment.simulation_count)
            self.assertEqual(EntityStatus.SUCCEEDED, experiment.simulations[0].status)

            with self.subTest("test_model_sweep_reload_simulation_task"):
                experiment_reload = Experiment.from_id(experiment.uid, load_task=True)
                self.assertEqual(experiment.id, experiment_reload.id)
                self.assertEqual(1, experiment_reload.assets.count)
                self.assertEqual(experiment.simulation_count, experiment_reload.simulation_count)
                self.assertEqual(experiment.succeeded, experiment_reload.succeeded)
                for sim in experiment_reload.simulations:
                    self.assertEqual(0, sim.assets.count)
                    self.assertIn('a', sim.task.parameters)
                    self.assertIn('a', sim.tags)
                    self.assertEqual(sim.tags['a'], sim.task.parameters['a'])

            with self.subTest("test_model_sweep_reload_simulation"):
                experiment_reload = Experiment.from_id(experiment.uid)
                self.assertEqual(experiment.id, experiment_reload.id)
                self.assertEqual(1, experiment_reload.assets.count)
                self.assertEqual(experiment.simulation_count, experiment_reload.simulation_count)
                self.assertEqual(experiment.succeeded, experiment_reload.succeeded)
                self.assertEqual(experiment.simulations[0].task.command, experiment_reload.simulations[0].task.command)
                self.assertEqual(1, experiment_reload.simulations[0].assets.count)
