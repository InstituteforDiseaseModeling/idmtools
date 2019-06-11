import copy
import os
import unittest

from idmtools.core import EntityStatus
from idmtools.entities import ExperimentBuilder
from idmtools.managers import ExperimentManager
from idmtools.platforms import COMPSPlatform
from idmtools_models.python import PythonExperiment
from tests import INPUT_PATH
from tests.utils.decorators import comps_test
from tests.utils.ITestWithPersistence import ITestWithPersistence


@comps_test
class TestCOMPSPlatform(ITestWithPersistence):
    def setUp(self) -> None:
        super().setUp()
        self.platform = COMPSPlatform(endpoint="https://comps2.idmod.org", environment="Bayesian")

        def setP(simulation, p):
            return simulation.set_parameter("P", p)

        self.builder = ExperimentBuilder()
        self.builder.add_sweep_definition(setP, [1, 2, 3])

    def _run_and_test_experiment(self, experiment):
        experiment.builder = self.builder

        # Create experiment on platform
        experiment.pre_creation()
        self.platform.create_experiment(experiment)

        # Create the simulations on the platform
        experiment.execute_builder()

        # Dispatch events
        for simulation in experiment.simulations:
            simulation.pre_creation()

        self.platform.create_simulations(experiment)
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
        experiment = PythonExperiment(name="Test Python Experiment Success",
                                      model_path=os.path.join(INPUT_PATH, "compsplatform", "working_model.py"))
        self._run_and_test_experiment(experiment)
        self.assertTrue(all([s.status == EntityStatus.SUCCEEDED for s in experiment.simulations]))

    def test_status_retrieval_failed(self):
        experiment = PythonExperiment(name="Test Python Experiment Failed",
                                      model_path=os.path.join(INPUT_PATH, "compsplatform", "failing_model.py"))
        self._run_and_test_experiment(experiment)
        self.assertTrue(all([s.status == EntityStatus.FAILED for s in experiment.simulations]))
        self.assertFalse(experiment.succeeded)

    def test_status_retrieval_mixed(self):
        experiment = PythonExperiment(name="Test Python Experiment Mixed",
                                      model_path=os.path.join(INPUT_PATH, "compsplatform", "mixed_model.py"))
        self._run_and_test_experiment(experiment)
        self.assertTrue(experiment.done)
        self.assertFalse(experiment.succeeded)
        for s in experiment.simulations:
            self.assertTrue(s.tags["P"] == 2 and s.status == EntityStatus.FAILED or s.status == EntityStatus.SUCCEEDED)

    def test_from_experiment(self):
        experiment = PythonExperiment(name="Test Python Experiment Mixed",
                                      model_path=os.path.join(INPUT_PATH, "compsplatform", "mixed_model.py"))
        self._run_and_test_experiment(experiment)
        experiment2 = copy.deepcopy(experiment)
        experiment2.simulations.clear()
        self.platform.restore_simulations(experiment2)

        self.assertEqual(len(experiment.simulations), len(experiment2.simulations))


if __name__ == '__main__':
    unittest.main()
