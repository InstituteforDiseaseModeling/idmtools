import copy
import json
import os
import unittest
from os import path

import pytest
from idmtools.builders import SimulationBuilder
from idmtools.core import EntityStatus
from idmtools.entities.experiment import Experiment
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_platform_comps.comps_platform import COMPSPlatform
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.common_experiments import wait_on_experiment_and_check_all_sim_status
from idmtools_test.utils.comps import assure_running_then_wait_til_done, setup_test_with_platform_and_simple_sweep
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools.utils.filter_simulations import FilterItem

current_directory = path.dirname(path.realpath(__file__))


@pytest.mark.comps
class TestCOMPSPlatform(ITestWithPersistence):
    def setUp(self) -> None:
        super().setUp()
        self.platform: COMPSPlatform = None
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        setup_test_with_platform_and_simple_sweep(self)

    @pytest.mark.assets
    @pytest.mark.python
    @pytest.mark.long
    @pytest.mark.smoke
    def test_output_files_retrieval(self):
        config = {"a": 1, "b": 2}
        experiment = self.get_working_model_experiment(config)
        wait_on_experiment_and_check_all_sim_status(self, experiment, self.platform)
        experiment = Experiment.from_id(experiment.id, self.platform)
        files_needed = ["config.json", "Assets\\working_model.py"]
        self.platform.get_files(item=experiment.simulations[0], files=files_needed)

        # Call twice to see if the cache is actually leveraged
        files_retrieved = self.platform.get_files(item=experiment.simulations[0], files=files_needed)

        # We have the correct files?
        self.assertEqual(len(files_needed), len(files_retrieved))

        # Test the content
        with open(os.path.join(COMMON_INPUT_PATH, "compsplatform", "working_model.py"), 'rb') as m:
            self.assertEqual(files_retrieved["Assets\\working_model.py"], m.read())
        self.assertEqual(files_retrieved["config.json"], json.dumps(config).encode('utf-8'))

        # Test different separators
        files_needed = ["Assets/working_model.py"]
        files_retrieved = self.platform.get_files(item=experiment.simulations[0], files=files_needed)

        # We have the correct files?
        self.assertEqual(len(files_needed), len(files_retrieved))

        # Test the content
        with open(os.path.join(COMMON_INPUT_PATH, "compsplatform", "working_model.py"), 'rb') as m:
            self.assertEqual(files_retrieved["Assets/working_model.py"], m.read())

        # Test wrong filename
        files_needed = ["Assets/bad.py", "bad.json"]
        with self.assertRaises(RuntimeError):
            self.platform.get_files(item=experiment.simulations[0], files=files_needed)

    def get_working_model_experiment(self, config=None, script="working_model.py") -> Experiment:
        if config is None:
            config = dict()
        model_path = os.path.join(COMMON_INPUT_PATH, "compsplatform", script)
        task = JSONConfiguredPythonTask(script_path=model_path, parameters=config)
        experiment = Experiment.from_task(task, name=self.case_name)
        return experiment

    def _run_and_test_experiment(self, experiment):
        experiment.platform = self.platform
        experiment.builder = self.builder

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

        self.platform.refresh_status(item=experiment)

        # Test if we have all simulations at status CREATED
        self.assertFalse(experiment.done)
        self.assertTrue(all([s.status == EntityStatus.CREATED for s in experiment.simulations]))

        # Start experiment
        assure_running_then_wait_til_done(self, experiment)

    @pytest.mark.long
    def test_status_retrieval_succeeded(self):
        experiment = self.get_working_model_experiment()
        wait_on_experiment_and_check_all_sim_status(self, experiment, self.platform)

    @pytest.mark.long
    def test_status_retrieval_failed(self):
        experiment = self.get_working_model_experiment(script='failing_model.py')
        wait_on_experiment_and_check_all_sim_status(self, experiment, self.platform,
                                                    expected_status=EntityStatus.FAILED)

    @pytest.mark.long
    def test_status_retrieval_mixed(self):
        model_path = os.path.join(COMMON_INPUT_PATH, "compsplatform", 'mixed_model.py')
        task = JSONConfiguredPythonTask(script_path=model_path)
        builder = SimulationBuilder()
        builder.add_sweep_definition(JSONConfiguredPythonTask.set_parameter_partial('P'), range(3))
        experiment = Experiment.from_builder(builder, task, name=self.case_name)
        experiment.run(wait_until_done=True)
        self.assertTrue(experiment.done)
        self.assertFalse(experiment.succeeded)

        if len(experiment.simulations) == 0:
            raise Exception('NO CHILDREN')

        self.assertEqual(len(experiment.simulations), 3)
        for s in experiment.simulations:
            self.assertTrue((s.tags["P"] == 2 and s.status == EntityStatus.FAILED) or  # noqa: W504
                            (s.status == EntityStatus.SUCCEEDED))

    @pytest.mark.long
    def test_from_experiment(self):
        experiment = self.get_working_model_experiment()
        wait_on_experiment_and_check_all_sim_status(self, experiment, self.platform)

        experiment2 = copy.deepcopy(experiment)
        experiment2.platform = self.platform

        # very explicitly clearing the stored children and re-querying
        experiment2.simulations.clear()
        experiment2.refresh_simulations()

        self.assertTrue(len(experiment.simulations) > 0)
        self.assertEqual(len(experiment.simulations), len(experiment2.simulations))
        self.assertTrue(experiment2.done)
        self.assertTrue(experiment2.succeeded)

    @pytest.mark.long
    def test_filter_status_for_succeeded_sims(self):
        model_path = os.path.join(COMMON_INPUT_PATH, "compsplatform", 'mixed_model.py')
        task = JSONConfiguredPythonTask(script_path=model_path)
        builder = SimulationBuilder()
        builder.add_sweep_definition(JSONConfiguredPythonTask.set_parameter_partial('P'), range(3))
        experiment = Experiment.from_builder(builder, task, name=self.case_name)
        experiment.run(wait_until_done=True)
        self.assertTrue(experiment.done)
        self.assertFalse(experiment.succeeded)

        # only get back the succeeded sims
        sims = FilterItem.filter_item(self.platform, experiment, status=EntityStatus.SUCCEEDED)
        self.assertEqual(len(sims), 2)

    def test_experiment_name(self):  # zdu: no metadata file any more
        model_path = os.path.join(COMMON_INPUT_PATH, "compsplatform", "working_model.py")
        task = JSONConfiguredPythonTask(script_path=model_path, envelope="parameters")
        e = Experiment.from_task(task, name="test/\\:'?<>*\|name1()δ`")
        e.run(wait_until_done=True)
        self.assertTrue(e.succeeded)
        name_expected = 'test__________name1___'
        self.assertEqual(e.name, name_expected)
        self.assertIsNone(e.simulations[0].name)

    def test_experiment_simulation_name_cleanup(self):
        model_path = os.path.join(COMMON_INPUT_PATH, "python", "hello_world.py")
        task = JSONConfiguredPythonTask(script_path=model_path, parameters={})
        name = ""
        s = ['/', '\\', ':', "'", '"', '?', '<', '>', '*', '|', "\0"]
        exp_name = name.join(s)
        experiment = Experiment.from_task(task, name=self.case_name + "_name" + exp_name + "test")
        experiment.simulations[0].name = "test/\\:'?<>*|sim1"
        experiment.run(wait_until_done=True)
        name_expected = self.case_name + "_name___________test"
        self.assertEqual(experiment.name, name_expected)
        self.assertEqual(experiment.simulations[0].name, "test_________sim1")


if __name__ == '__main__':
    unittest.main()
