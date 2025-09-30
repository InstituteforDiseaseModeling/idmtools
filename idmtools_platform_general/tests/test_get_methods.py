import copy
import os
import sys
import unittest

import pytest
from functools import partial
from typing import Any, Dict, List

from idmtools.entities.command_task import CommandTask
from idmtools.entities.generic_workitem import GenericWorkItem
from idmtools.utils.collections import ExperimentParentIterator

if sys.platform == "win32":
    from win32con import FALSE
from idmtools.builders import SimulationBuilder
from idmtools.core import ItemType, EntityContainer
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
        #suite = self.platform.get_item("3887be47-a464-4abe-a2c2-a726798e556d", item_type=ItemType.SUITE, force=True)
        #experiment = suite.get_experiments()[0]
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
        print("test_get_simulations_file")
        print(repr(self.experiment))
        print(repr(file_experiment))
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
        experiment.parent = suite
        self.assertTrue(isinstance(suite, Suite))
        # Test Suite's get_experiments(), expect result is list of Experiments
        experiments = suite.get_experiments()
        self.assertTrue(all(isinstance(exp, Experiment) for exp in experiments))
        self.assertFalse(all(isinstance(exp, FileExperiment) for exp in experiments))
        self.assertEqual(experiments, suite.experiments)

    def test_get_experiments_file(self):
        experiment = self.experiment
        suite = experiment.suite
        print("test_get_experiments_file")
        print(repr(suite))
        print(repr(experiment))
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
        suite = self.platform.get_item(suite.id, item_type=ItemType.SUITE, force=True)
        exps = suite.get_experiments()
        exps_property = suite.experiments
        self.assertEqual(exps, exps_property)
        self.assertEqual(len(exps), 1)
        self.assertTrue(all(isinstance(exp, Experiment) for exp in exps))

        file_suite = self.platform.get_item(suite.id, item_type=ItemType.SUITE, raw=True)
        file_exps = file_suite.get_experiments()
        self.assertEqual(len(file_exps), 1)
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
        self.assertEqual(len(sims), 9)
        self.assertTrue(all(isinstance(sim, Simulation) for sim in sims.items))
        file_experiment = self.platform.get_item(experiment.id, item_type=ItemType.EXPERIMENT, raw=True)
        file_sims = file_experiment.get_simulations()
        self.assertTrue(isinstance(file_sims, List))
        self.assertEqual(len(file_sims), 9)
        self.assertTrue(all(isinstance(sim, FileSimulation) for sim in file_sims))

        # set simulations = []
        experiment.simulations = []
        sims = experiment.get_simulations()
        self.assertTrue(len(sims) == 0)

    def test_get_experiments_with_no_platform(self):
        suite = Suite("my suite")
        experiment = Experiment("my experiment")
        suite.add_experiment(experiment)
        experiments = suite.get_experiments()
        self.assertTrue(isinstance(experiments, EntityContainer))

    def test_get_simulations_with_no_platform(self):
        experiment = Experiment("my experiment")
        simulation1 = Simulation("my sim1")
        simulation2 = Simulation("my sim2")
        experiment.add_simulation(simulation1)
        experiment.add_simulation(simulation2)
        simulations = experiment.get_simulations()
        self.assertTrue(isinstance(simulations, ExperimentParentIterator))

    def test_add_experiment(self):
        experiment = self.create_experiment(a=2, b=2)
        suite: Suite = experiment.parent
        task = CommandTask(command='python --version')
        new_experiment1 = Experiment.from_task(task=task, name='new experiment1')
        new_experiment2 = Experiment.from_task(task=task, name='new experiment2')
        suite.add_experiment(experiment)
        suite.add_experiment(new_experiment1)
        suite.add_experiment(new_experiment2)
        exps = suite.get_experiments()
        self.assertEqual(len(exps), 3)
        self.assertTrue(all(isinstance(exp, Experiment) for exp in exps))
        self.assertEqual(repr(suite), f"<Suite {suite.id} - 3 experiments>")

    @pytest.mark.skip("Only run this in local with valid experiment id")
    def test_add_experiment_file(self):
        experiment = self.create_experiment(a=2, b=2)
        suite: Suite = experiment.parent
        file_suite = suite.get_platform_object()
        new_experiment_file = self.platform.get_item("e8161f68-7fcc-4bd5-992d-247f842da2a0", item_type=ItemType.EXPERIMENT, raw=True, force=True)
        file_suite.add_experiment(new_experiment_file)
        file_exps = file_suite.get_experiments()
        self.assertEqual(len(file_exps), 2)
        self.assertTrue(all(isinstance(exp, FileExperiment) for exp in file_exps))
        self.assertEqual(repr(file_suite), f"<FileSuite {file_suite.id} - 2 experiments>")

    def test_add_simulation(self):
        experiment = self.create_experiment(a=2, b=2)
        new_simulation1 = Simulation("my sim1")
        new_simulation2 = Simulation("my sim2")
        experiment.add_simulation(new_simulation1)
        experiment.add_simulation(new_simulation2)
        sims = experiment.get_simulations()
        self.assertEqual(len(sims), 6)
        self.assertTrue(all(isinstance(sim, Simulation) for sim in sims))
        self.assertEqual(repr(experiment), f'<Experiment: {experiment.id} - test_experiment / Sim count 6>')

    @pytest.mark.skip("Only run this in local with valid experiment id")
    def test_add_simulation_file(self):
        experiment = self.create_experiment(a=2, b=2)
        file_experiment = experiment.get_platform_object()
        new_simulation_file = self.platform.get_item("2c7dea18-5a70-4e2e-95fc-f1e09f214423", item_type=ItemType.SIMULATION, raw=True, force=True)
        file_experiment.add_simulation(new_simulation_file)
        file_experiment.add_simulation("4baf88f9-d655-4583-8979-76f4b4c00c73")
        file_sims = file_experiment.get_simulations()
        self.assertEqual(len(file_sims), 6)
        self.assertTrue(all(isinstance(sim, FileSimulation) for sim in file_sims))
        self.assertEqual(repr(file_experiment), f'<FileExperiment {file_experiment.id} - 6 simulations>')

    def test_get_tags_experiments(self):
        experiment = self.experiment
        # Test get_tags for base experiment
        tags = experiment.get_tags()
        tags_p = experiment.tags
        expected_subset_tags = {'tag1': 1}
        self.assertTrue(all(tags.get(k) == v for k, v in expected_subset_tags.items()))
        self.assertDictEqual(tags, tags_p)

        # Test get_tags for file experiment
        file_experiment = experiment.get_platform_object()
        tags_f = file_experiment.get_tags()
        tags_f_p = file_experiment.tags
        self.assertTrue(all(tags_f.get(k) == v for k, v in expected_subset_tags.items()))
        self.assertDictEqual(tags_f, tags_p)
        self.assertDictEqual(tags_f_p, tags_p)

        # Test update_tags for base experiment
        experiment = self.experiment
        experiment.update_tags({"a": 2})
        tags1 = experiment.get_tags()
        expected_subset_tags = {'tag1': 1, "a": 2}
        self.assertTrue(all(tags1.get(k) == v for k, v in expected_subset_tags.items()))
        # Test update_tags for file experiment
        file_experiment = self.experiment.get_platform_object()
        file_experiment.update_tags({"file_tags": "c"})
        tags_f1 = file_experiment.get_tags()
        expected_subset_tags = {'tag1': 1, "file_tags": "c"}
        self.assertTrue(all(tags_f1.get(k) == v for k, v in expected_subset_tags.items()))

    def test_get_tags_simulations(self):
        experiment = self.experiment
        simulations = experiment.get_simulations()
        for sim in simulations:
            tags = sim.get_tags()
            self.assertIn('a', tags)
            self.assertIn('b', tags)
            # Check values are in desired range
            self.assertIn(tags['a'], range(3))
            self.assertIn(tags['b'], range(3))
        file_simulations = experiment.get_platform_object().get_simulations()
        for sim in file_simulations:
            tags = sim.get_tags()
            self.assertIn('a', tags)
            self.assertIn('b', tags)
            # Check values are in desired range
            self.assertIn(tags['a'], range(3))
            self.assertIn(tags['b'], range(3))

        # Test update tags for base simulation
        simulations = experiment.get_simulations()
        for sim in simulations:
            sim.update_tags({"c": 100})
            tags = sim.get_tags()
            self.assertIn("c", tags)
            self.assertEqual(tags["c"], 100)
            self.assertIn('a', tags)
            self.assertIn('b', tags)
            # Check values are in desired range
            self.assertIn(tags['a'], range(3))
            self.assertIn(tags['b'], range(3))

        # Test update tags for file simulation
        file_simulations = experiment.get_platform_object().get_simulations()
        for sim in file_simulations:
            sim.update_tags({"d": 200})
            tags = sim.get_tags()
            self.assertIn("d", tags)
            self.assertEqual(tags["d"], 200)
            self.assertIn('a', tags)
            self.assertIn('b', tags)
            # Check values are in desired range
            self.assertIn(tags['a'], range(3))
            self.assertIn(tags['b'], range(3))

    def test_get_tags_suite(self):
        suite: Suite = self.experiment.parent
        # Test base suite's get_tags()
        tags = suite.get_tags()
        expected_suite_tags = {'name': 'suite_tag', 'idmtools': '123'}
        self.assertTrue(all(tags.get(k) == v for k, v in expected_suite_tags.items()))
        # Test file suite's get_tags
        file_suite = suite.get_platform_object()
        tags_f = file_suite.get_tags()
        expected_suite_tags = {'name': 'suite_tag', 'idmtools': '123'}
        self.assertTrue(all(tags_f.get(k) == v for k, v in expected_suite_tags.items()))
        # Test update_tags
        suite: Suite = self.experiment.parent
        suite.update_tags({"new_suite_tag": 321})
        tags = suite.get_tags()
        expected_suite_tags = {'name': 'suite_tag', 'idmtools': '123', "new_suite_tag": 321}
        self.assertTrue(all(tags.get(k) == v for k, v in expected_suite_tags.items()))

        # Test update_tags for file_suite
        file_suite = self.experiment.parent.get_platform_object()
        file_suite.update_tags({"new_file_suite_tag": "abc"})
        tags = file_suite.get_tags()
        expected_suite_tags = {'name': 'suite_tag', 'idmtools': '123', "new_file_suite_tag": "abc"}
        self.assertTrue(all(tags.get(k) == v for k, v in expected_suite_tags.items()))

    def test_duplicate_simulation_not_added_twice(self):
        exp = Experiment("expB")
        sim = Simulation("sim1")

        exp.add_simulation(sim)
        exp.add_simulation(sim)

        assert len(exp.simulations) == 1