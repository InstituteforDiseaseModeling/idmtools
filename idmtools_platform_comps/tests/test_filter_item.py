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
class TestCompsFilterItem(ITestWithPersistence):

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

    def find_matched_sims_status(self, simulations, status):
        matched_sim_ids = []
        for sim in simulations:
            if sim.status == status:  # matched status
                matched_sim_ids.append(sim.id)
        return matched_sim_ids

    def find_matched_sims_tags(self, simulations, tags):
        matched_sim_ids = []
        for sim in simulations:
            if all(k in sim.tags and sim.tags[k] == v for k, v in tags.items()):  # matched tags
                matched_sim_ids.append(sim.id)
        return matched_sim_ids


    @classmethod
    def setUpClass(cls):
        cls.platform = Platform('SlurmStage')
        cls.suite = cls._run_create_test_experiments(cls)
        cls.experiment = cls.suite.experiments[0]

    def setUp(self) -> None:
        self.case_name = get_case_name(os.path.basename(__file__) + "--" + self._testMethodName)
        self.experiment = self.platform.get_item(self.experiment.id, item_type=ItemType.EXPERIMENT, force=True)
        print(self.case_name)

    # Filter from Suite
    # Test default filter with suite uuid and type which only returns succeed sims (2 in this case)
    def test_filter_item_by_id_suite_tags(self):
        actual_result = FilterItem.filter_item_by_id(self.platform, self.suite.uid, ItemType.SUITE,
                                            tags={'tag1': 1})
        actual_result_tag_string = FilterItem.filter_item_by_id(self.platform, self.suite.uid, ItemType.SUITE,
                                            tags={'tag1': "1"})
        potential_simulations = self.platform.flatten_item(self.suite, raw=False)
        expected_sim_ids = self.find_matched_sims_tags(potential_simulations, {'tag1': "1"})
        actual_sim_ids = actual_result[self.suite.experiments[0].id]
        self.assertEqual(len(actual_sim_ids), len(expected_sim_ids))
        self.assertEqual(len(actual_sim_ids), 5)
        self.assertSetEqual(set(actual_result[self.experiment.id]), set(expected_sim_ids))
        self.assertSetEqual(set(actual_result_tag_string[self.experiment.id]), set(expected_sim_ids))


    # test filter with suite which only return succeed sims by default
    def test_filter_item_suite_status(self):
        suite = self.platform.get_item(self.suite.uid, ItemType.SUITE, raw=False)
        actual_result = FilterItem.filter_item(self.platform, suite, status=EntityStatus.SUCCEEDED)
        potential_simulations = self.platform.flatten_item(self.suite, raw=False)
        expected_sim_ids = self.find_matched_sims_status(potential_simulations, status=EntityStatus.SUCCEEDED)
        actual_sim_ids = actual_result[self.experiment.id]
        self.assertSetEqual(set(actual_sim_ids), set(expected_sim_ids))
        self.assertEqual(len(actual_result[self.experiment.id]), 2)

    # test filter with experiment and status=failed which only return failed sims(3 in this case)
    def test_filter_item_experiment_status(self):
        exp = self.experiment
        actual_result = FilterItem.filter_item(self.platform, exp, status=EntityStatus.FAILED, max_simulations=5)
        self.assertEqual(len(actual_result), 3)
        potential_simulations = self.platform.flatten_item(exp, raw=False)
        expected_sim_ids = self.find_matched_sims_status(potential_simulations, status=EntityStatus.FAILED)
        self.assertSetEqual(set(actual_result), set(expected_sim_ids))

    # test filter with experiment and tags which only return 1 matched succeed sim
    def test_filter_item_experiment_tags(self):
        exp = self.experiment
        actual_sims = FilterItem.filter_item(self.platform, exp,  tags={"Run_Number": lambda v: 1 <= v < 3}, entity_type=True)
        potential_simulations = self.platform.flatten_item(exp, raw=False)
        expected_sims = []
        for sim in potential_simulations:
            if sim.tags.get("Run_Number")=="1" or sim.tags.get("Run_Number")=="2":
                expected_sims.append(sim)
        self.assertEqual(len(actual_sims), 2)
        self.assertSetEqual(set([sim.id for sim in actual_sims]), set([sim.id for sim in expected_sims]))

    # test filter with experiment and max_simulations filter which only return 1 matched succeed sim
    def test_filter_item_experiment_max(self):
        exp = self.experiment
        actual_sims = FilterItem.filter_item(self.platform, exp, max_simulations=1)
        self.assertEqual(len(actual_sims), 1)

    # test filter with experiment and skip_sims filter which only return 1 matched succeed sim (another one skipped)
    def test_filter_experiment_skip(self):
        # Filter from Experiment
        skip_sim = str(self.experiment.simulations[1].uid)
        actual_sims = FilterItem.filter_item_by_id(self.platform, self.experiment.uid, ItemType.EXPERIMENT,
                                            skip_sims=[skip_sim], max_simulations=5)
        potential_simulations = self.platform.flatten_item(self.experiment, raw=False)
        potential_simulation_ids = [sim.id for sim in potential_simulations]
        potential_simulation_ids.remove(skip_sim)
        self.assertEqual(len(actual_sims), len(potential_simulation_ids))
        self.assertSetEqual(set(actual_sims), set(potential_simulation_ids))

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
