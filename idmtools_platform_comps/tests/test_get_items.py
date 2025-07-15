import allure
import unittest
import pytest
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.entities.simulation import Simulation


@pytest.mark.comps
@pytest.mark.python
@allure.story("COMPS")
@allure.story("Python")
@allure.suite("idmtools_platform_comps")
class TestGetItems(unittest.TestCase):
    def setUp(self) -> None:
        self.platform = Platform('SlurmStage')

    def test_get_experiments_and_get_simulations(self):
        experiment = self.platform.get_item("6a1bc8c0-4f47-f011-9310-f0921c167864", item_type=ItemType.EXPERIMENT)
        suite = self.platform.get_item("691bc8c0-4f47-f011-9310-f0921c167864", item_type=ItemType.SUITE, force=True)  # force=True to avoid cache from above line
        simulations = experiment.simulations
        # Test get_simulations and simulations from experiment, should be the same
        simulations_1 = experiment.get_simulations()
        self.assertTrue(all(isinstance(sim, Simulation) for sim in simulations_1.items))
        # make sure simulation ids are the same between simulations_1 and simulations
        simulations_1_ids = [sim.id for sim in simulations_1.items]
        simulations_ids = [sim.id for sim in simulations.items]
        self.assertSetEqual(set(simulations_1_ids), set(simulations_ids))

        # Test get_experiments and experiments from suite, should be the same
        experiments = suite.get_experiments()
        experiments_1 = suite.experiments
        self.assertTrue(len(experiments), 1)
        self.assertTrue(len(experiments_1), 1)
        self.assertEqual(experiments, experiments_1)

        # Test get_simulations from comps experiment
        comps_experiment = experiment.get_platform_object()
        comps_simulations = comps_experiment.get_simulations()
        comps_simulation_ids = [str(sim.id) for sim in comps_simulations]
        self.assertSetEqual(set(comps_simulation_ids), set(simulations_1_ids))


if __name__ == '__main__':
    unittest.main()