import copy
import json
import os
import unittest
from os import path

import pytest

from idmtools.core import EntityStatus
from idmtools_platform_comps.comps_platform import COMPSPlatform
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.comps import assure_running_then_wait_til_done, setup_test_with_platform_and_simple_sweep
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence

current_directory = path.dirname(path.realpath(__file__))


@pytest.mark.comps
class TestCOMPSPlatform(ITestWithPersistence):
    def setUp(self) -> None:
        super().setUp()
        self.platform: COMPSPlatform = None
        setup_test_with_platform_and_simple_sweep(self)

    @pytest.mark.assets
    @pytest.mark.python
    @pytest.mark.long
    def test_output_files_retrieval(self):
        config = {"a": 1, "b": 2}
        experiment = PythonExperiment(name=self.case_name,
                                      model_path=os.path.join(COMMON_INPUT_PATH, "compsplatform", "working_model.py"))
        experiment.base_simulation.parameters = config
        em = ExperimentManager(experiment, platform=self.platform)
        em.run()
        em.wait_till_done()

        from idmtools.utils.entities import retrieve_experiment
        experiment = retrieve_experiment(experiment.uid, platform=self.platform, with_simulations=True)
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
        experiment = PythonExperiment(name=self.case_name,
                                      model_path=os.path.join(COMMON_INPUT_PATH, "compsplatform", "working_model.py"))
        self._run_and_test_experiment(experiment)
        print([s.status for s in experiment.simulations])
        self.assertTrue(all([s.status == EntityStatus.SUCCEEDED for s in experiment.simulations]))

    @pytest.mark.long
    def test_status_retrieval_failed(self):
        experiment = PythonExperiment(name=self.case_name,
                                      model_path=os.path.join(COMMON_INPUT_PATH, "compsplatform", "failing_model.py"))
        self._run_and_test_experiment(experiment)
        self.assertTrue(all([s.status == EntityStatus.FAILED for s in experiment.simulations]))
        self.assertFalse(experiment.succeeded)

    @pytest.mark.long
    def test_status_retrieval_mixed(self):
        experiment = PythonExperiment(name=self.case_name,
                                      model_path=os.path.join(COMMON_INPUT_PATH, "compsplatform", "mixed_model.py"))
        self._run_and_test_experiment(experiment)
        self.assertTrue(experiment.done)
        self.assertFalse(experiment.succeeded)

        if len(experiment.simulations) == 0:
            raise Exception('NO CHILDREN')

        for s in experiment.simulations:
            self.assertTrue((s.tags["P"] == 2 and s.status == EntityStatus.FAILED) or  # noqa: W504
                            (s.status == EntityStatus.SUCCEEDED))

    @pytest.mark.long
    def test_from_experiment(self):
        experiment = PythonExperiment(name=self.case_name,
                                      model_path=os.path.join(COMMON_INPUT_PATH, "compsplatform", "working_model.py"))
        self._run_and_test_experiment(experiment)
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
    def test_experiment_manager(self):
        experiment = PythonExperiment(name=self.case_name,
                                      model_path=os.path.join(COMMON_INPUT_PATH, "compsplatform", "working_model.py"))
        experiment.platform = self.platform
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
