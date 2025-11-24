import os
import pathlib
import sys
import unittest

import pytest
from functools import partial
from typing import Any, Dict
from idmtools.entities.generic_workitem import GenericWorkItem
if sys.platform == "win32":
    from win32con import FALSE
from idmtools.builders import SimulationBuilder
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.entities import Suite
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_platform_file.platform_operations.utils import FileSimulation, FileExperiment, FileSuite
from idmtools_test import COMMON_INPUT_PATH


@pytest.mark.serial
class TestFilePlatform(unittest.TestCase):

    def create_experiment(self, a=1, b=1, retries=None, wait_until_done=False):
        task = JSONConfiguredPythonTask(script_path=os.path.join(COMMON_INPUT_PATH, "python", "model3.py"),
                                        envelope="parameters", parameters=(dict(c=0)))
        task.python_path = "python3"

        ts = TemplatedSimulations(base_task=task)
        builder = SimulationBuilder()

        def param_update(simulation: Simulation, param: str, value: Any) -> Dict[str, Any]:
            return simulation.task.set_parameter(param, value)

        builder.add_sweep_definition(partial(param_update, param="a"), range(a))
        builder.add_sweep_definition(partial(param_update, param="b"), range(b))
        ts.add_builder(builder)

        # Now we can create our Experiment using our template builder
        experiment = Experiment.from_template(ts, name="test_experiment")
        # Add our own custom tag to simulation
        experiment.tags["tag1"] = 1
        # And add common assets from local dir
        experiment.assets.add_directory(assets_directory=os.path.join(COMMON_INPUT_PATH, "python", "Assets"))

        # Create suite
        suite = Suite(name='Idm Suite')
        suite.update_tags({'name': 'suite_tag', 'idmtools': '123'})
        # Add experiment to the suite
        suite.add_experiment(experiment)
        # Commission
        suite.run(wait_until_done=wait_until_done, retries=retries)
        print("suite_id: " + suite.id)
        print("experiment_id: " + experiment.id)
        return experiment

    @classmethod
    def setUpClass(cls) -> None:
        cls.job_directory = "DEST"
        cls.platform = Platform('Container', job_directory=cls.job_directory)
        cls.experiment = cls.create_experiment(cls, a=3, b=3)

    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName

    def test_get_directory_with_suite(self):
        experiment = self.experiment
        suite: Suite = experiment.parent
        file_suite: FileSuite = suite.get_platform_object()
        # Verify get_directory for server suite (file_suite)
        self.assertEqual(self.platform.get_directory(file_suite), file_suite.get_directory())
        # verify get_directory for local suite (idmtools suite)
        self.assertEqual(self.platform.get_directory(suite), suite.get_directory())

        self.assertEqual(self.platform.get_directory(suite), self.platform.get_directory(file_suite))
        # create a random suite object:
        suite = Suite(name="my_suite")
        try:
            suite.get_directory()
        except AttributeError as e:
            self.assertTrue(f"Suite id: {suite.id} not found in ContainerPlatform." in str(e))

    def test_get_directory_with_exp(self):
        experiment = self.experiment
        file_experiment = experiment.get_platform_object()
        # verify get_directory for server experiment (file_experiment)
        self.assertEqual(self.platform.get_directory(file_experiment), file_experiment.get_directory())
        # verify get_directory for local experiment (idmtools experiment)
        self.assertEqual(self.platform.get_directory(experiment), experiment.get_directory())
        self.assertEqual(experiment.directory, experiment.get_directory())
        # create a random experiment object:
        exp = Experiment(name="my_exp")
        try:
            exp.get_directory()
        except AttributeError as e:
            self.assertTrue(f"Experiment id: {exp.id} not found in ContainerPlatform." in str(e))

    def test_get_directory_with_sim(self):
        experiment = self.experiment
        file_sim: FileSimulation = self.platform.get_item(experiment.simulations[0].id, item_type=ItemType.SIMULATION,
                                                          raw=True)
        # verify get_directory for server sim (file_sim)
        self.assertEqual(file_sim.get_directory(), self.platform.get_directory(file_sim))
        self.assertEqual(file_sim.get_directory(), file_sim.directory)
        idmtools_sim: Simulation = self.platform.get_item(experiment.simulations[0].id,
                                                              item_type=ItemType.SIMULATION,
                                                              raw=False)
        # verify get_directory for local sim (idmtools sim)
        self.assertEqual(idmtools_sim.get_directory(), self.platform.get_directory(idmtools_sim))
        self.assertEqual(idmtools_sim.directory, idmtools_sim.get_directory())

        # create a random simulation object:
        sim = Simulation(name="my_sim")
        try:
            sim.get_directory()
        except RuntimeError as e:
            self.assertTrue("Simulation missing parent!" in str(e))

    def test_get_directory_workitem(self):
        workitem = GenericWorkItem(name="test_workitem")
        try:
            workitem.get_directory()
        except Exception as e:
            self.assertTrue("Only support Suite/Experiment/Simulation for get_directory() for now." in str(e))

    def test_get_simulations(self):
        experiment = self.experiment
        # Test Experiment's get_simulations(), expect result is list of Simulations
        simulations = experiment.get_simulations()
        self.assertTrue(all(isinstance(sim, Simulation) for sim in simulations.items))
        self.assertFalse(all(isinstance(sim, FileSimulation) for sim in simulations.items))
        self.assertEqual(simulations.items, experiment.simulations.items)

    def test_get_simulations_file(self):
        file_experiment = self.experiment.get_platform_object()
        self.assertTrue(isinstance(file_experiment, FileExperiment))
        # Test FileExperiment's get_simulations(), expect result is list of FileSimulations
        file_simulations = file_experiment.get_simulations()
        self.assertTrue(all(isinstance(sim, FileSimulation) for sim in file_simulations))
        # make sure simulation ids are the same between file_simulations and self.experiment.simulations
        file_sim_ids = [sim.id for sim in file_simulations]
        converted_sim_ids = [sim.id for sim in self.experiment.simulations.items]
        self.assertSetEqual(set(file_sim_ids), set(converted_sim_ids))

    def test_get_experiments(self):
        experiment = self.experiment
        suite = experiment.suite
        self.assertTrue(isinstance(suite, Suite))
        # Test Suite's get_experiments(), expect result is list of Experiments
        experiments = suite.get_experiments()
        self.assertTrue(all(isinstance(exp, Experiment) for exp in experiments))
        self.assertFalse(all(isinstance(exp, FileExperiment) for exp in experiments))
        self.assertEqual(experiments, suite.experiments)

    def test_get_experiments_file(self):
        experiment = self.experiment
        suite = experiment.suite
        file_suite = suite.get_platform_object()
        self.assertTrue(isinstance(file_suite, FileSuite))
        # Test FileSuite's get_experiments(), expect result is list of FileExperiments
        file_experiments = file_suite.get_experiments()
        self.assertTrue(all(isinstance(exp, FileExperiment) for exp in file_experiments))
        file_exp_ids = [exp.id for exp in file_experiments]
        converted_exp_ids = [exp.id for exp in suite.experiments]
        self.assertSetEqual(set(file_exp_ids), set(converted_exp_ids))

    def test_get_directory_before_and_after_run(self):
        task = JSONConfiguredPythonTask(script_path=os.path.join(COMMON_INPUT_PATH, "python", "model3.py"), envelope="parameters", parameters=(dict(c=0)))
        experiment = Experiment.from_task(task, name="test_dir")
        # test get_directory before run
        exp_dir = experiment.get_directory()
        self.assertEqual(exp_dir, pathlib.Path(os.path.join(os.path.dirname(os.path.abspath(__file__)), self.job_directory, f"e_test_dir_{experiment.id}")))
        experiment.assets.add_directory(assets_directory=os.path.join(COMMON_INPUT_PATH, "python", "Assets"))
        suite = Suite(name='my_suite')
        experiment.parent = suite
        suite.run(platform=self.platform, wait_until_done=False)
        # test get_directory after run
        exp_dir_again = experiment.get_directory()
        self.assertEqual(exp_dir_again, pathlib.Path(os.path.join(os.path.dirname(os.path.abspath(__file__)), self.job_directory, f"s_my_suite_{suite.id}", f"e_test_dir_{experiment.id}")))


