import allure
import os
import unittest
from functools import partial
from idmtools.builders import SimulationBuilder
from idmtools.core import ItemType, EntityStatus
from idmtools.core.platform_factory import Platform
from idmtools.entities import Suite
from idmtools.entities.experiment import Experiment
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools.utils.filter_simulations import FilterItem
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_platform_file.platform_operations.utils import FileSimulation, FileSuite
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools_test.utils.utils import get_case_name


@allure.story("Python")
@allure.story("Filtering")
@allure.suite("idmtools_platform_container")
class TestSimulations(ITestWithPersistence):

    def _run_create_test_experiments(self):
        """
        create suite and experiment with 5 simulations. 2 succeed ones and 3 failed ones
        :return: ExperimentManager
        """
        def param_update(simulation, param, value):
            return simulation.task.set_parameter(param, value)
        setA = partial(param_update, param="Run_Number")

        task = JSONConfiguredPythonTask(
            script_path=os.path.join(COMMON_INPUT_PATH, "python_experiments", "model.py"))
        ts = TemplatedSimulations(base_task=task)
        # We can define common metadata like tags across all the simulations using the base_simulation object
        ts.base_simulation.tags['tag1'] = 1

        # Since we have our templated simulation object now, let's define our sweeps
        # To do that we need to use a builder
        builder = SimulationBuilder()
        builder.add_sweep_definition(setA, range(5))
        ts.add_builder(builder)
        experiment = Experiment(name="test_filter_simulations.py--test_experiment", simulations=ts)
        suite = Suite(name='test_filter_simulations.py--test suite')
        suite.update_tags({'name': 'test', 'fetch': 123})
        self.platform.create_items([suite])
        suite.add_experiment(experiment)
        experiment.run(wait_until_done=True)
        # suite_id = 'd35b322e-4238-f011-930f-f0921c167860'
        # suite = self.platform.get_item(suite_id, item_type=ItemType.SUITE)
        return suite

    @classmethod
    def setUpClass(cls):
        cls.platform = Platform('Container', job_directory="DEST")
        cls.suite = cls._run_create_test_experiments(cls)
        cls.experiment = cls.suite.experiments[0]

    def setUp(self) -> None:
        self.case_name = get_case_name(os.path.basename(__file__) + "--" + self._testMethodName)
        print(self.case_name)

    # Filter from Experiment, self.experiment has 5 simulations includes 2 succeed sims and 3 failed sims
    # Test default filter with experiment uuid and type which only returns succeed sims (2 in this case)
    def test_filter_experiment(self):
        sims = FilterItem.filter_item_by_id(self.platform, self.experiment.uid, ItemType.EXPERIMENT, max_simulations=5)
        self.assertEqual(len(sims), 2)

    # Filter from Suite
    # Test default filter with suite uuid and type which only returns succeed sims (2 in this case)
    def test_filter_suite(self):
        sims = FilterItem.filter_item_by_id(self.platform, self.suite.uid, ItemType.SUITE)
        self.assertEqual(len(sims), 2)

    # Test default filter plus tags which only returns 1 matched succeed sims
    def test_filter_item_experiment(self):
        exp = self.platform.get_item(self.experiment.uid, ItemType.EXPERIMENT, raw=False)
        sims = FilterItem.filter_item(self.platform, exp, max_simulations=5, tags={'Run_Number': 1})
        self.assertEqual(len(sims), 1)

    # test filter with suite which only return succeed sims by default
    def test_filter_item_suite(self):
        suite = self.platform.get_item(self.suite.uid, ItemType.SUITE, raw=False)
        sims = FilterItem.filter_item(self.platform, suite)
        self.assertEqual(len(sims), 2)

    # test filter with experiment and status=failed which only return failed sims(3 in this case)
    def test_filter_item_experiment_status(self):
        exp = self.platform.get_item(self.experiment.uid, ItemType.EXPERIMENT, raw=False)
        sims = FilterItem.filter_item(self.platform, exp, max_simulations=5, status=EntityStatus.FAILED)
        self.assertEqual(len(sims), 3)

    # test filter with experiment and tags which only return 1 matched succeed sim
    def test_filter_item_experiment_tags(self):
        exp = self.platform.get_item(self.experiment.uid, ItemType.EXPERIMENT, raw=False)
        sims = FilterItem.filter_item(self.platform, exp, max_simulations=5, tags={'Run_Number': 1})
        self.assertEqual(len(sims), 1)

    # test filter with experiment and max_simulations filter which only return 1 matched succeed sim
    def test_filter_item_experiment_max(self):
        exp = self.platform.get_item(self.experiment.uid, ItemType.EXPERIMENT, raw=False)
        sims = FilterItem.filter_item(self.platform, exp, max_simulations=1)
        self.assertEqual(len(sims), 1)

    # test filter with experiment and skip_sims filter which only return 1 matched succeed sim (another one skipped)
    def test_filter_experiment_skip(self):
        # Filter from Experiment
        skip_sim = str(self.experiment.simulations[1].uid)
        sims = FilterItem.filter_item_by_id(self.platform, self.experiment.uid, ItemType.EXPERIMENT,
                                            skip_sims=[skip_sim], max_simulations=5)
        self.assertEqual(len(sims), 1)

    # def test_flatten_item_idm_suite(self):
    #     flatten_items = self.platform.flatten_item(self.suite)
    #     self.assertEqual(len(flatten_items), 5)
    #     for item in flatten_items:
    #         self.assertTrue(isinstance(item, Simulation))
    #
    # def test_flatten_item_file_suite(self):
    #     file_suite = self.platform.get_item(self.suite.id, item_type=ItemType.SUITE, raw=True)
    #     flatten_items = self.platform.flatten_item(file_suite, raw=True)
    #     self.assertEqual(len(flatten_items), 5)
    #     for item in flatten_items:
    #         self.assertTrue(isinstance(item, FileSimulation))
    #
    # def test_flatten_item_file_suite_raw_false(self):
    #     file_suite = self.platform.get_item(self.suite.id, item_type=ItemType.SUITE, raw=True)
    #     flatten_items = self.platform.flatten_item(file_suite, raw=False)
    #     self.assertEqual(len(flatten_items), 5)
    #     for item in flatten_items:
    #         self.assertTrue(isinstance(item, Simulation))
    #
    # def test_flatten_item_idm_experiment(self):
    #     flatten_items = self.platform.flatten_item(self.experiment)
    #     self.assertEqual(len(flatten_items), 5)
    #     for item in flatten_items:
    #         self.assertTrue(isinstance(item, Simulation))
    #
    # def test_flatten_item_file_experiment(self):
    #     file_exp = self.platform.get_item(self.experiment.id, item_type=ItemType.EXPERIMENT, raw=True)
    #     flatten_items = self.platform.flatten_item(file_exp, raw=True)
    #     self.assertEqual(len(flatten_items), 5)
    #     for item in flatten_items:
    #         self.assertTrue(isinstance(item, FileSimulation))
    #
    # def test_flatten_item_idm_simulation(self):
    #     flatten_items = self.platform.flatten_item(self.experiment.simulations[0])
    #     self.assertEqual(len(flatten_items), 1)
    #     for item in flatten_items:
    #         self.assertTrue(isinstance(item, Simulation))
    #
    # def test_flatten_item_file_simulation(self):
    #     file_sim = self.platform.get_item(self.experiment.simulations[0].id, item_type=ItemType.SIMULATION, raw=True)
    #     flatten_items = self.platform.flatten_item(file_sim, raw=True)
    #     self.assertEqual(len(flatten_items), 1)
    #     for item in flatten_items:
    #         self.assertTrue(isinstance(item, FileSimulation))
    def test_get_directory_with_suite(self):
        suite: Suite = self.experiment.parent
        file_suite: FileSuite = suite.get_platform_object()
        # verify get_directory for server suite (file_suite)
        self.assertEqual(self.platform.get_directory(file_suite), file_suite.get_directory())
        self.assertEqual(self.platform.directory(file_suite), self.platform.get_directory(file_suite))
        # verify get_directory for local suite (idmtools suite)
        self.assertEqual(self.platform.directory(suite), suite.get_directory())
        self.assertEqual(self.platform.directory(suite), self.platform.get_directory(suite))

        self.assertEqual(self.platform.directory(suite), self.platform.get_directory(file_suite))

    def test_get_directory_with_exp(self):
        file_experiment = self.platform.get_item(self.experiment.id, item_type=ItemType.EXPERIMENT, raw=True)
        # verify get_directory for server experiment (file_experiment)
        self.assertEqual(self.platform.get_directory(file_experiment), file_experiment.get_directory())
        self.assertEqual(self.platform.directory(file_experiment), self.platform.get_directory(file_experiment))
        # verify get_directory for local experiment (idmtools experiment)
        self.assertEqual(self.platform.directory(self.experiment), self.experiment.get_directory())
        self.assertEqual(self.platform.directory(self.experiment), self.platform.get_directory(self.experiment))

        self.assertEqual(self.platform.directory(self.experiment), self.platform.get_directory(file_experiment))

    def test_get_directory_with_sim(self):
        file_sim: FileSimulation = self.platform.get_item(self.experiment.simulations[0].id, item_type=ItemType.SIMULATION, raw=True)
        # verify get_directory for server sim (file_sim)
        self.assertEqual(self.platform.directory(file_sim), self.platform.get_directory(file_sim))
        self.assertEqual(self.platform.directory(file_sim), file_sim.get_directory())
        idmtools_sim: FileSimulation = self.experiment.simulations[0]
        # verify get_directory for local sim (idmtools sim)
        print(idmtools_sim.get_directory())
        self.assertEqual(self.platform.directory(idmtools_sim), self.platform.get_directory(idmtools_sim))
        self.assertEqual(self.platform.directory(idmtools_sim), idmtools_sim.get_directory())

        self.assertEqual(self.platform.directory(file_sim), self.platform.get_directory(idmtools_sim))


if __name__ == '__main__':
    unittest.main()
