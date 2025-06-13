import os
import allure
import unittest
import pytest
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.entities.simulation import Simulation
from idmtools_test.utils.utils import get_case_name


@pytest.mark.comps
@pytest.mark.python
@allure.story("COMPS")
@allure.story("Python")
@allure.suite("idmtools_platform_comps")
class TestGetItems(unittest.TestCase):
    def setUp(self) -> None:
        self.case_name = get_case_name(os.path.basename(__file__) + "--" + self._testMethodName)
        print(self.case_name)
        self.platform = Platform('SlurmStage')

    def test_get_experiments_and_get_simulations(self):
        experiment = self.platform.get_item("6a1bc8c0-4f47-f011-9310-f0921c167864", item_type=ItemType.EXPERIMENT)
        suite = self.platform.get_item("691bc8c0-4f47-f011-9310-f0921c167864", item_type=ItemType.SUITE)
        simulations = experiment.simulations
        # Test get_simulations
        simulations_1 = experiment.get_simulations()
        self.assertTrue(all(isinstance(sim, Simulation) for sim in simulations_1.items))
        # make sure simulation ids are the same between simulations_1 and simulations
        simulations_1_ids = [sim.id for sim in simulations_1.items]
        simulations_ids = [sim.id for sim in simulations.items]
        self.assertSetEqual(set(simulations_1_ids), set(simulations_ids))

        # Test get_experiments from suite
        experiments = suite.get_experiments()
        experiments_id = [exp.id for exp in experiments]
        self.assertEqual(experiments[0], experiment)

        # Test get_simulations from platform._experiments
        simulations_2 = self.platform._experiments.get_simulations(experiment)
        self.assertTrue(all(isinstance(sim, Simulation) for sim in simulations_2))
        # make sure simulation ids are the same between simulations_1 and simulations
        simulations_2_ids = [sim.id for sim in simulations_2]
        self.assertSetEqual(set(simulations_2_ids), set(simulations_ids))

        # Test get_experiments from platform._suites
        experiments_2 = self.platform._suites.get_experiments(suite)
        self.assertEqual(experiments, experiments_2)

        # Test get_simulations from comps experiment
        comps_experiment = experiment.get_platform_object()
        comps_simulations = comps_experiment.get_simulations()
        comps_simulation_ids = [str(sim.id) for sim in comps_simulations]
        self.assertSetEqual(set(comps_simulation_ids), set(simulations_2_ids))

        # Test get_experiments from comps suite
        comps_suite = suite.get_platform_object()
        comps_experiments = comps_suite.get_experiments()
        comps_experiment_ids = [str(exp.id) for exp in comps_experiments]
        self.assertSetEqual(set(comps_experiment_ids), set(experiments_id))


if __name__ == '__main__':
    unittest.main()