import copy
import json
import os
import unittest

from idmtools.builders import ExperimentBuilder
from idmtools.core import EntityStatus
from idmtools.managers import ExperimentManager
from idmtools.platforms import COMPSPlatform
from idmtools_models.python import PythonExperiment
from tests import INPUT_PATH
from tests.utils.decorators import comps_test
from tests.utils.ITestWithPersistence import ITestWithPersistence

current_directory = os.path.dirname(os.path.realpath(__file__))


@comps_test
class TestCOMPSPlatform(ITestWithPersistence):
    def setUp(self) -> None:
        super().setUp()
        self.platform = COMPSPlatform()
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        print(self.case_name)

        def setP(simulation, p):
            return simulation.set_parameter("P", p)

        self.builder = ExperimentBuilder()
        self.builder.add_sweep_definition(setP, [1, 2, 3])

    def test_output_files_retrieval(self):
        config = {"a": 1, "b": 2}
        experiment = PythonExperiment(name=self.case_name,
                                      model_path=os.path.join(INPUT_PATH, "compsplatform", "working_model.py"))
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
        with open(os.path.join(INPUT_PATH, "compsplatform", "working_model.py"), 'rb') as m:
            self.assertEqual(files_retrieved["Assets\\working_model.py"], m.read())
        self.assertEqual(files_retrieved["config.json"], json.dumps(config).encode('utf-8'))

        # Test different separators
        files_needed = ["Assets/working_model.py"]
        files_retrieved = self.platform.get_assets_for_simulation(experiment.simulations[0], files_needed)

        # We have the correct files?
        self.assertEqual(len(files_needed), len(files_retrieved))

        # Test the content
        with open(os.path.join(INPUT_PATH, "compsplatform", "working_model.py"), 'rb') as m:
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
                                      model_path=os.path.join(INPUT_PATH, "compsplatform", "working_model.py"))
        self._run_and_test_experiment(experiment)
        self.assertTrue(all([s.status == EntityStatus.SUCCEEDED for s in experiment.simulations]))

    def test_status_retrieval_failed(self):
        experiment = PythonExperiment(name=self.case_name,
                                      model_path=os.path.join(INPUT_PATH, "compsplatform", "failing_model.py"))
        self._run_and_test_experiment(experiment)
        self.assertTrue(all([s.status == EntityStatus.FAILED for s in experiment.simulations]))
        self.assertFalse(experiment.succeeded)

    def test_status_retrieval_mixed(self):
        experiment = PythonExperiment(name=self.case_name,
                                      model_path=os.path.join(INPUT_PATH, "compsplatform", "mixed_model.py"))
        self._run_and_test_experiment(experiment)
        self.assertTrue(experiment.done)
        self.assertFalse(experiment.succeeded)
        for s in experiment.simulations:
            self.assertTrue(s.tags["P"] == 2 and s.status == EntityStatus.FAILED or s.status == EntityStatus.SUCCEEDED)

    def test_from_experiment(self):
        experiment = PythonExperiment(name=self.case_name,
                                      model_path=os.path.join(INPUT_PATH, "compsplatform", "working_model.py"))
        self._run_and_test_experiment(experiment)
        experiment2 = copy.deepcopy(experiment)
        experiment2.simulations.clear()
        self.platform.restore_simulations(experiment2)

        self.assertEqual(len(experiment.simulations), len(experiment2.simulations))
        self.assertTrue(experiment2.done)
        self.assertTrue(experiment2.succeeded)


if __name__ == '__main__':
    unittest.main()
