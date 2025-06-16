import os
import sys
import unittest

import pytest
from functools import partial
from typing import Any, Dict, List
from idmtools.entities.generic_workitem import GenericWorkItem
from idmtools.utils.collections import ExperimentParentIterator

if sys.platform == "win32":
    from win32con import FALSE
from idmtools.builders import SimulationBuilder
from idmtools.core import ItemType, EntityContainer, UnknownItemException
from idmtools.core.platform_factory import Platform
from idmtools.entities import Suite
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_platform_file.platform_operations.utils import FileSimulation, FileExperiment, FileSuite
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.decorators import linux_only


@pytest.mark.serial
@linux_only
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
        cls.platform = Platform('FILE', job_directory=cls.job_directory)
        cls.experiment = cls.create_experiment(cls, a=3, b=3)

    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName

    def test_get_directory_with_suite(self):
        experiment = self.experiment
        suite: Suite = experiment.parent
        file_suite: FileSuite = suite.get_platform_object()
        # verify get_directory for server suite (file_suite)
        self.assertEqual(self.platform.get_directory(file_suite), file_suite.get_directory())
        # verify get_directory for local suite (idmtools suite)
        self.assertEqual(self.platform.get_directory(suite), suite.get_directory())

        self.assertEqual(self.platform.get_directory(suite), self.platform.get_directory(file_suite))
        # create a random suite object:
        suite = Suite(name="my_suite")
        try:
            suite.get_directory()
        except AttributeError as e:
            self.assertTrue(f"Suite id: {suite.id} not found in FilePlatform." in str(e))

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
            self.assertTrue(f"Experiment id: {exp.id} not found in FilePlatform." in str(e))

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
        except AttributeError as e:
            self.assertTrue(f"Simulation id: {sim.id} not found in FilePlatform." in str(e))

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

    def test_get_experiments_by_platform_get_items(self):
        experiment = self.experiment
        suite = experiment.suite
        suite = self.platform.get_item(suite.id, item_type=ItemType.SUITE)
        exps = suite.get_experiments()
        exps_property = suite.experiments
        self.assertEqual(exps, exps_property)
        self.assertTrue(isinstance(exps, EntityContainer))
        self.assertTrue(len(exps) == 1)
        self.assertTrue(all(isinstance(exp, Experiment) for exp in exps))

        file_suite = self.platform.get_item(suite.id, item_type=ItemType.SUITE, raw=True)
        file_exps = file_suite.get_experiments()
        self.assertTrue(len(file_exps) == 1)
        self.assertTrue(all(isinstance(exp, FileExperiment) for exp in file_exps))
        self.assertTrue(isinstance(file_exps, List))

    def test_get_simulations_by_platform_get_item(self):
        experiment = self.experiment
        experiment = self.platform.get_item(experiment.id, item_type=ItemType.EXPERIMENT, raw=False)
        sims = experiment.get_simulations()
        sims_property = experiment.simulations
        # verify experiment.get_simulations and experiment.simulations are the same
        self.assertEqual(sims.items, sims_property.items)
        self.assertTrue(isinstance(sims, ExperimentParentIterator))
        self.assertTrue(len(sims) == 9)
        self.assertTrue(all(isinstance(sim, Simulation) for sim in sims.items))
        file_experiment = self.platform.get_item(experiment.id, item_type=ItemType.EXPERIMENT, raw=True)
        file_sims = file_experiment.get_simulations()
        self.assertTrue(isinstance(file_sims, List))
        self.assertTrue(len(file_sims) == 9)
        self.assertTrue(all(isinstance(sim, FileSimulation) for sim in file_sims))

        # set simulations = []
        experiment.simulations = []
        sims = experiment.get_simulations()
        self.assertTrue(len(sims) == 0)

    def test_get_experiments_with_no_platform(self):
        suite = Suite("my suite")
        experiment = Experiment("my experiment")
        suite.add_experiment(experiment)
        with self.assertRaises(UnknownItemException) as context:
            experiments = suite.get_experiments()
        self.assertTrue(f"Suite my suite cannot retrieve experiments because it was not found on the platform." in str(context.exception.args[0]))

    def test_get_simulations_with_no_platform(self):
        experiment = Experiment("my experiment")
        simulation1 = Simulation("my sim1")
        simulation2 = Simulation("my sim2")
        experiment.add_simulation(simulation1)
        experiment.add_simulation(simulation2)
        with self.assertRaises(UnknownItemException) as context:
            simulations = experiment.get_simulations()
        self.assertTrue(f"Experiment my experiment cannot retrieve simulations because it was not found on the platform." in str(context.exception.args[0]))