import allure
import os
import unittest
from functools import partial
from idmtools.builders import SimulationBuilder
from idmtools.core import ItemType, EntityStatus
from idmtools.core.platform_factory import Platform
from idmtools.entities import Suite
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools.utils.filter_simulations import FilterItem
from COMPS.Data import Simulation as COMPSSimulation
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools_test.utils.utils import get_case_name


@allure.story("COMPS")
@allure.story("Python")
@allure.story("Filtering")
@allure.suite("idmtools_platform_comps")
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
        suite.add_experiment(experiment)
        suite.run(wait_until_done=True)
        # suite_id = 'd35b322e-4238-f011-930f-f0921c167860'
        # suite = self.platform.get_item(suite_id, item_type=ItemType.SUITE)
        return suite

    @classmethod
    def setUpClass(cls):
        cls.platform = Platform('SlurmStage')
        cls.suite = cls._run_create_test_experiments(cls)
        cls.experiment = cls.suite.experiments[0]

    def setUp(self) -> None:
        self.case_name = get_case_name(os.path.basename(__file__) + "--" + self._testMethodName)
        self.experiment = self.platform.get_item(self.experiment.id, item_type=ItemType.EXPERIMENT, force=True)
        print(self.case_name)

    # Filter from Experiment, self.experiment has 5 simulations includes 2 succeed sims and 3 failed sims
    # Test default filter with experiment uuid and type which only returns succeed sims (2 in this case)
    def test_filter_experiment(self):
        sims = FilterItem.filter_item_by_id(self.platform, self.experiment.id, ItemType.EXPERIMENT, max_simulations=5,
                                            status=EntityStatus.SUCCEEDED)
        self.assertEqual(len(sims), 2)

    # Filer from Suite
    # Test default filter with suite uuid and type which only returns succeed sims (2 in this case)
    def test_filter_item_by_id_suite_tag1(self):
        exp_sims = FilterItem.filter_item_by_id(self.platform, self.suite.uid, ItemType.SUITE,
                                            tags={'tag1': 1})
        self.assertEqual(len(exp_sims[self.suite.experiments[0].id]), 5)

    # Test default filter plus tags which only returns 1 matched succeed sims
    def test_filter_item_experiment(self):
        exp = self.experiment
        sims = FilterItem.filter_item(self.platform, exp, max_simulations=5, tags={'Run_Number': '1'})
        self.assertEqual(len(sims), 1)

    # test filter with suite which only return succeed sims by default
    def test_filter_item_suite_status(self):
        suite = self.platform.get_item(self.suite.uid, ItemType.SUITE, force=True)
        exp_sims = FilterItem.filter_item(self.platform, suite, status=EntityStatus.SUCCEEDED)
        self.assertEqual(len(exp_sims[self.suite.experiments[0].id]), 2)

    # test filter with experiment and status=failed which only return failed sims(3 in this case)
    def test_filter_item_experiment_status(self):
        exp = self.experiment
        sims = FilterItem.filter_item(self.platform, exp, status=EntityStatus.FAILED, max_simulations=5)
        self.assertEqual(len(sims), 3)

    # test filter with experiment and tags which only return 1 matched succeed sim
    def test_filter_item_experiment_tags(self):
        exp = self.experiment
        sims = FilterItem.filter_item(self.platform, exp, tags={'Run_Number': '1'}, max_simulations=5)
        self.assertEqual(len(sims), 1)

    # test filter with experiment and max_simulations filter which only return 1 matched succeed sim
    def test_filter_item_experiment_max(self):
        exp = self.experiment
        sims = FilterItem.filter_item(self.platform, exp, max_simulations=1)
        self.assertEqual(len(sims), 1)

    # test filter with experiment and skip_sims filter which only return 1 matched succeed sim (another one skipped)
    def test_filter_experiment_skip(self):
        # Filter from Experiment
        skip_sim = str(self.experiment.simulations[1].uid)
        sims = FilterItem.filter_item_by_id(self.platform, self.experiment.uid, ItemType.EXPERIMENT,
                                            skip_sims=[skip_sim], max_simulations=5)
        self.assertEqual(len(sims), 4)

    def test_flatten_item_idm_suite(self):
        flatten_items = self.platform.flatten_item(self.suite)
        self.assertEqual(len(flatten_items), 5)
        for item in flatten_items:
            self.assertTrue(isinstance(item, Simulation))

    def test_flatten_item_comps_suite(self):
        comps_suite = self.platform.get_item(self.suite.id, item_type=ItemType.SUITE, raw=True)
        flatten_items = self.platform.flatten_item(comps_suite)
        self.assertEqual(len(flatten_items), 5)
        for item in flatten_items:
            self.assertTrue(isinstance(item, Simulation))

    def test_flatten_item_idm_experiment(self):
        flatten_items = self.platform.flatten_item(self.experiment)
        self.assertEqual(len(flatten_items), 5)
        for item in flatten_items:
            self.assertTrue(isinstance(item, Simulation))

    def test_flatten_item_comps_experiment(self):
        comps_exp = self.platform.get_item(self.experiment.id, item_type=ItemType.EXPERIMENT, raw=True)
        flatten_items = self.platform.flatten_item(comps_exp, raw=True)
        self.assertEqual(len(flatten_items), 5)
        for item in flatten_items:
            self.assertTrue(isinstance(item, COMPSSimulation))

    def test_flatten_item_idm_simulation(self):
        flatten_items = self.platform.flatten_item(self.experiment.simulations[0])
        self.assertEqual(len(flatten_items), 1)
        for item in flatten_items:
            self.assertTrue(isinstance(item, Simulation))

    def test_flatten_item_comps_simulation(self):
        comps_sim = self.platform.get_item(self.experiment.simulations[0].id, item_type=ItemType.SIMULATION, raw=True)
        flatten_items = self.platform.flatten_item(comps_sim, raw=True)
        self.assertEqual(len(flatten_items), 1)
        for item in flatten_items:
            self.assertTrue(isinstance(item, COMPSSimulation))


if __name__ == '__main__':
    unittest.main()
