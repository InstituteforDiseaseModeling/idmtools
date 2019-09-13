import copy
import json
import os
import unittest
from os import path
import pytest
from idmtools.core.platform_factory import Platform
from idmtools.builders import ExperimentBuilder
from idmtools.core import EntityStatus
from idmtools.managers import ExperimentManager
from idmtools_models.python import PythonExperiment
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools_test import COMMON_INPUT_PATH

current_directory = path.dirname(path.realpath(__file__))


@pytest.mark.comps
class TestCOMPSPlatform(ITestWithPersistence):
    def setUp(self) -> None:
        super().setUp()
        self.platform = Platform('COMPS2')
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        print(self.case_name)

        def setP(simulation, p):
            return simulation.set_parameter("P", p)

        self.builder = ExperimentBuilder()
        self.builder.add_sweep_definition(setP, [1, 2, 3])

    def test_output_files_retrieval(self):
        config = {"a": 1, "b": 2}
        experiment = PythonExperiment(name=self.case_name,
                                      model_path=os.path.join(COMMON_INPUT_PATH, "compsplatform", "working_model.py"))
        experiment.base_simulation.parameters = config
        em = ExperimentManager(experiment=experiment, platform=self.platform)
        em.run()
        em.wait_till_done()

        from idmtools.utils.entities import retrieve_experiment
        experiment = retrieve_experiment(experiment.uid, platform=self.platform, with_simulations=True)
        files_needed = ["config.json", "Assets\\working_model.py"]
        self.platform.get_assets_for_simulation(experiment.simulations[0], files_needed)

        # Call twice to see if the cache is actually leveraged
        files_retrieved = self.platform.get_assets_for_simulation(experiment.simulations[0], files_needed)

        # We have the correct files?
        self.assertEqual(len(files_needed), len(files_retrieved))

        # Test the content
        with open(os.path.join(COMMON_INPUT_PATH, "compsplatform", "working_model.py"), 'rb') as m:
            self.assertEqual(files_retrieved["Assets\\working_model.py"], m.read())
        self.assertEqual(files_retrieved["config.json"], json.dumps(config).encode('utf-8'))

        # Test different separators
        files_needed = ["Assets/working_model.py"]
        files_retrieved = self.platform.get_assets_for_simulation(experiment.simulations[0], files_needed)

        # We have the correct files?
        self.assertEqual(len(files_needed), len(files_retrieved))

        # Test the content
        with open(os.path.join(COMMON_INPUT_PATH, "compsplatform", "working_model.py"), 'rb') as m:
            self.assertEqual(files_retrieved["Assets/working_model.py"], m.read())

        # Test wrong filename
        files_needed = ["Assets/bad.py", "bad.json"]
        with self.assertRaises(RuntimeError):
            self.platform.get_assets_for_simulation(experiment.simulations[0], files_needed)

    def _run_and_test_experiment(self, experiment):
        experiment.builder = self.builder

        # Create experiment on platform
        experiment.pre_creation()
        self.platform.create_experiment(experiment)

        for simulation_batch in experiment.batch_simulations(batch_size=10):
            # Create the simulations on the platform
            for simulation in simulation_batch:
                simulation.pre_creation()

            ids = self.platform.create_simulations(simulation_batch)

            for uid, simulation in zip(ids, simulation_batch):
                simulation.uid = uid
                simulation.post_creation()
                experiment.simulations.append(simulation)

        self.platform.refresh_experiment_status(experiment)

        # Test if we have all simulations at status CREATED
        self.assertFalse(experiment.done)
        self.assertTrue(all([s.status == EntityStatus.CREATED for s in experiment.simulations]))

        # Start experiment
        self.platform.run_simulations(experiment)
        self.platform.refresh_experiment_status(experiment)
        self.assertFalse(experiment.done)
        self.assertTrue(all([s.status == EntityStatus.RUNNING for s in experiment.simulations]))

        # Wait till done
        import time
        start_time = time.time()
        while time.time() - start_time < 180:
            self.platform.refresh_experiment_status(experiment)
            if experiment.done:
                break
            time.sleep(3)
        self.assertTrue(experiment.done)

    def test_status_retrieval_succeeded(self):
        experiment = PythonExperiment(name=self.case_name,
                                      model_path=os.path.join(COMMON_INPUT_PATH, "compsplatform", "working_model.py"))
        self._run_and_test_experiment(experiment)
        self.assertTrue(all([s.status == EntityStatus.SUCCEEDED for s in experiment.simulations]))

    def test_status_retrieval_failed(self):
        experiment = PythonExperiment(name=self.case_name,
                                      model_path=os.path.join(COMMON_INPUT_PATH, "compsplatform", "failing_model.py"))
        self._run_and_test_experiment(experiment)
        self.assertTrue(all([s.status == EntityStatus.FAILED for s in experiment.simulations]))
        self.assertFalse(experiment.succeeded)

    def test_status_retrieval_mixed(self):
        experiment = PythonExperiment(name=self.case_name,
                                      model_path=os.path.join(COMMON_INPUT_PATH, "compsplatform", "mixed_model.py"))
        self._run_and_test_experiment(experiment)
        self.assertTrue(experiment.done)
        self.assertFalse(experiment.succeeded)
        for s in experiment.simulations:
            self.assertTrue(s.tags["P"] == 2 and s.status == EntityStatus.FAILED or s.status == EntityStatus.SUCCEEDED)

    def test_from_experiment(self):
        experiment = PythonExperiment(name=self.case_name,
                                      model_path=os.path.join(COMMON_INPUT_PATH, "compsplatform", "working_model.py"))
        self._run_and_test_experiment(experiment)
        experiment2 = copy.deepcopy(experiment)
        experiment2.simulations.clear()
        self.platform.restore_simulations(experiment2)

        self.assertEqual(len(experiment.simulations), len(experiment2.simulations))
        self.assertTrue(experiment2.done)
        self.assertTrue(experiment2.succeeded)

    def test_experiment_manager(self):
        experiment = PythonExperiment(name=self.case_name,
                                      model_path=os.path.join(COMMON_INPUT_PATH, "compsplatform", "working_model.py"))
        self._run_and_test_experiment(experiment)
        em = ExperimentManager.from_experiment_id(experiment.uid, self.platform)

        # Verify new ExperimentManager contains correct info
        # For experiment in newly created em, it only restore same experiment id ro pythonexperiment
        # For simulations in newly created em, simulation id/tags/status should be retrieved to pythonsimulation
        self.assertEqual(em.experiment.base_simulation, experiment.base_simulation)
        self.assertEqual(em.experiment.uid, experiment.uid)
        self.assertEqual(em.experiment.tags, experiment.tags)
        self.assertEqual(em.platform, self.platform)
        for i in range(len(em.experiment.simulations)):
            self.assertEqual(em.experiment.simulations[i].uid, experiment.simulations[i].uid)
            self.assertEqual(em.experiment.simulations[i].tags["P"], str(i + 1))
            # self.assertDictEqual(em.experiment.simulations[i].tags, experiment.simulations[i].tags)
            self.assertEqual(em.experiment.simulations[i].status, experiment.simulations[i].status)


if __name__ == '__main__':
    unittest.main()
