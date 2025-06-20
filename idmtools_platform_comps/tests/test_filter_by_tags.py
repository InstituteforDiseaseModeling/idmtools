import os
import sys
import tempfile
import unittest
import re
from functools import partial

from idmtools.builders import SimulationBuilder
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.entities import Suite
from idmtools.entities.simulation import Simulation
from idmtools_test.utils.common_experiments import \
    wait_on_experiment_and_check_all_sim_status, get_model1_templated_experiment

sys.path.insert(0, os.path.dirname(__file__))


uuid_pattern = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE
)


class TestSimulationsWithTags(unittest.TestCase):

    def create_experiment(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            exp = get_model1_templated_experiment("test_filter_by_tags")

            def param_update_ab(simulation, param, value):
                # Set B within
                if param == "a":
                    simulation.task.set_parameter("b", value + 2)

                return {"a": value, "b": value + 2}

            setAB = partial(param_update_ab, param="a")

            builder = SimulationBuilder()
            # Sweep parameter "a" and make "b" depends on "a"
            builder.add_sweep_definition(setAB, range(0, 6))
            exp.simulations.add_builder(builder)
            wait_on_experiment_and_check_all_sim_status(self, exp)
            # exp = self.platform.get_item("0f8ccd95-104e-f011-9311-f0921c167864", item_type=ItemType.EXPERIMENT)
            return exp

    @classmethod
    def setUpClass(cls) -> None:
        cls.platform = Platform('SlurmStage')
        cls.exp = cls.create_experiment(cls)

    def setUp(self):
        self.experiment = self.platform.get_item(self.exp.id, item_type=ItemType.EXPERIMENT, force=True)

    def test_tag_filter_with_range(self):
        experiment = self.platform.get_item("d9cb76d9-e9e6-ee11-9301-f0921c167864", ItemType.EXPERIMENT)
        filter_simulation_ids = experiment.simulations_with_tags(
            tags={"__sample_index__": lambda v: 4 <= v <= 10, "Reporting_Rate": 0.4})
        filter_simulation_ids1 = experiment.simulations_with_tags(
            tags={"__sample_index__": lambda v: 4 <= v <= 10, "Reporting_Rate": 0.4})
        self.assertEqual(len(filter_simulation_ids), 7)
        self.assertEqual(len(filter_simulation_ids1), 7)

        filter_simulation_ids2 = experiment.simulations_with_tags(
            tags={"__sample_index__": lambda v: 1 <= v <= "10", "Typhoid_Environmental_Exposure_Rate": lambda v: v >= 0.4})
        self.assertEqual(len(filter_simulation_ids2), 2)

        # Below call with entity_type=True will return matched simulation objects. Total count should be the same as above cases
        filter_simulations = experiment.simulations_with_tags(
            tags={"__sample_index__": lambda v: 4 <= v <= "10", "Reporting_Rate": "0.4"}, entity_type=True)
        count = 0
        for sim in filter_simulations:
            self.assertTrue(isinstance(sim, Simulation))
            count += 1
            print(sim.tags)
        self.assertEqual(len(filter_simulations), 7)

    def test_suite_sim_tags_by_id(self):
        experiment = self.experiment
        suite = Suite(name='Idm Suite')
        suite.add_experiment(experiment)
        expected = {"a": "0"}
        suite = experiment.parent
        # Let search tags with 2 different ways for int-like string.
        result = suite.simulations_with_tags(tags={"a": 0})
        result1 = suite.simulations_with_tags(tags={"a": "0"})
        self.assertEqual(result, result1)
        # make sure each simulation in result contains tag {"a": "0"}
        for sim_id in result[experiment.id]:
            self.assertTrue(uuid_pattern.match(sim_id))
            sim = self.platform.get_item(sim_id, item_type=ItemType.SIMULATION)
            assert all(item in sim.tags.items() for item in expected.items())
        # make sure we have 1 simulation matched
        self.assertEqual(len(result[experiment.id]), 1)

    def test_experiment_sim_tags_by_id(self):
        experiment = self.experiment
        # this returns list of simulation ids
        expected = {"a": "0"}
        simulation_ids = experiment.simulations_with_tags(tags={"a": "0"})
        simulation_ids_1 = experiment.simulations_with_tags(tags={"a": 0})
        # verify we can search both with int 0 and str "0"
        self.assertEqual(simulation_ids, simulation_ids_1)
        # make sure each simulation contains tag {"a": "0"} in returned simulations
        for sim_id in simulation_ids:
            self.assertTrue(uuid_pattern.match(sim_id))
            sim = self.platform.get_item(sim_id, item_type=ItemType.SIMULATION)
            for k, v in expected.items():
                self.assertIn(k, sim.tags)
                self.assertEqual(sim.tags[k], v)
        # make sure we have 0 simulations matched
        self.assertEqual(len(simulation_ids), 1)

    def test_suite_sim_tags_by_object(self):
        experiment = self.experiment
        suite = Suite(name='Idm Suite')
        suite.add_experiment(experiment)
        expected = {"a": "0"}
        suite = experiment.parent
        # this returns dict with experiment_id as key and list of simulation as value
        result_sim = suite.simulations_with_tags(tags={"a": 0, "b": 2}, entity_type=True)
        result_id = suite.simulations_with_tags(tags={"a": "0", "b": "2"}, entity_type=False)
        # make sure above 2 results basically return the same simulation
        self.assertEqual(result_sim[experiment.id][0].id, result_id[experiment.id][0])
        for sim in result_sim[experiment.id]:
            self.assertTrue(isinstance(sim, Simulation))
            for k, v in expected.items():
                self.assertIn(k, sim.tags)
                self.assertEqual(sim.tags[k], v)
        # make sure we have 1 simulation matched
        self.assertEqual(len(result_sim[experiment.id]), 1)

    def test_experiment_sim_tags_by_object(self):
        experiment = self.experiment
        # this returns list of simulation ids
        expected = {"a": "0"}
        simulation_ids = experiment.simulations_with_tags(tags=expected)
        # this returns list of simulations
        simulations = experiment.simulations_with_tags(tags=expected, entity_type=True)
        # validation--------------------------------------------
        # make sure each simulation contains tag {"a": "0"} in returned simulations
        for sim in simulations:
            self.assertTrue(isinstance(sim, Simulation))
            for k, v in expected.items():
                self.assertIn(k, sim.tags)
                self.assertEqual(sim.tags[k], v)
        # make sure we have 1 simulation matched
        self.assertEqual(len(simulations), 1)

    def test_suite_sim_tags_skip_sims(self):
        experiment = self.experiment
        suite = Suite(name='Idm Suite')
        suite.add_experiment(experiment)
        excluded = {"a": "1", "b": "3"}
        expected = {"a": "0", "b": "2"}
        # Collect simulation IDs where any excluded tag key-value pair matches
        skip_sims = [
            sim.id
            for sim in experiment.simulations
            if any(sim.tags.get(k) == v for k, v in excluded.items())
        ]
        suite = experiment.suite
        # this returns dict with experiment_id as key and list of simulation as value
        result = suite.simulations_with_tags(tags={"a": 0, "b": "2"}, skip_sims=skip_sims, entity_type=True)
        # validation--------------------------------------------
        # make sure each simulation contains tag {"a": 0, "b":2} and not contains {"a": 1, "b", 3} in returned simulations
        for sim in result[experiment.id]:
            self.assertTrue(isinstance(sim, Simulation))
            # make sure all simulation do not contain tags with {"b": 2}
            assert not all(item in sim.tags.items() for item in excluded.items())
            for k, v in expected.items():
                self.assertIn(k, sim.tags)
                self.assertEqual(sim.tags[k], v)
        # make sure we have 1 simulation matched
        self.assertEqual(len(result[experiment.id]), 1)

    def test_experiment_sim_tags_skip_sims(self):
        experiment = self.experiment
        # this returns list of simulations
        excluded = {"b": 5}
        expected = {"a": "0"}
        # skip simulations contain tags with {"b":2}
        skip_sims = [sim.id for sim in experiment.simulations if
                     any(sim.tags.get(k) == v for k, v in excluded.items())]
        simulations = experiment.simulations_with_tags(tags={"a": "0", "b": 2}, skip_sims=skip_sims, entity_type=True)
        # validation--------------------------------------------
        # make sure each simulation contains tag {"a": "0"} and not contains {"b": "5"} in returned simulations
        for sim in simulations:
            self.assertTrue(isinstance(sim, Simulation))
            assert not all(item in sim.tags.items() for item in {"b": "5"}.items())
            for k, v in expected.items():
                self.assertIn(k, sim.tags)
                self.assertEqual(sim.tags[k], v)
        # make sure we have 0 simulations matched
        self.assertEqual(len(simulations), 1)
