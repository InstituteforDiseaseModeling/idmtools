import os
import sys
import tempfile
import unittest
import re
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.entities.simulation import Simulation

sys.path.insert(0, os.path.dirname(__file__))
from helps import create_experiment

uuid_pattern = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE
)


class TestSimulationsWithTags(unittest.TestCase):

    def test_suite_sim_tags_by_id(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            platform = Platform('CONTAINER', job_directory=temp_dir)
            sys.path.insert(0, os.path.dirname(__file__))
            experiment = create_experiment()
            suite = experiment.suite
            # this returns dict with experiment_id as key and list of simulation ids as value
            result = suite.simulations_with_tags(tags={"a": 0})
            # validation--------------------------------------------
            expected = {"a": 0}
            # make sure each simulation in result contains tag {"a": 0}
            for sim_id in result[experiment.id]:
                self.assertTrue(uuid_pattern.match(sim_id))
                sim = platform.get_item(sim_id, item_type=ItemType.SIMULATION)
                assert all(item in sim.tags.items() for item in expected.items())
            # make sure we have 5 simulations matched
            self.assertEqual(len(result[experiment.id]), 5)

    def test_experiment_sim_tags_by_id(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            platform = Platform('CONTAINER', job_directory=temp_dir)
            sys.path.insert(0, os.path.dirname(__file__))
            experiment = create_experiment()
            # this returns list of simulation ids
            simulation_ids = experiment.simulations_with_tags(tags={"a": 0})
            # validation--------------------------------------------
            expected = {"a": 0}
            # make sure each simulation contains tag {"a": 0} in returned simulations
            for sim_id in simulation_ids:
                self.assertTrue(uuid_pattern.match(sim_id))
                sim = platform.get_item(sim_id, item_type=ItemType.SIMULATION)
                assert all(item in sim.tags.items() for item in expected.items())
            # make sure we have 5 simulations matched
            self.assertEqual(len(simulation_ids), 5)

    def test_suite_sim_tags_by_object(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            platform = Platform('CONTAINER', job_directory=temp_dir)
            sys.path.insert(0, os.path.dirname(__file__))
            experiment = create_experiment()
            suite = experiment.suite
            # this returns dict with experiment_id as key and list of simulation as value
            result = suite.simulations_with_tags(tags={"a": 0}, entity_type=True)
            expected = {"a": 0}
            # make sure each simulation in result contains tag {"a": 0}
            for sim in result[experiment.id]:
                self.assertTrue(isinstance(sim, Simulation))
                assert all(item in sim.tags.items() for item in expected.items())
            # make sure we have 5 simulations matched
            self.assertEqual(len(result[experiment.id]), 5)

    def test_experiment_sim_tags_by_object(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            platform = Platform('CONTAINER', job_directory=temp_dir)
            sys.path.insert(0, os.path.dirname(__file__))
            experiment = create_experiment()
            # this returns list of simulations
            simulations = experiment.simulations_with_tags(tags={"a": 0}, entity_type=True)
            # validation--------------------------------------------
            expected = {"a": 0}
            # make sure each simulation contains tag {"a": 0} in returned simulations
            for sim in simulations:
                self.assertTrue(isinstance(sim, Simulation))
                assert all(item in sim.tags.items() for item in expected.items())
            # make sure we have 5 simulations matched
            self.assertEqual(len(simulations), 5)

    def test_suite_sim_tags_skip_sims(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            platform = Platform('CONTAINER', job_directory=temp_dir)
            sys.path.insert(0, os.path.dirname(__file__))
            experiment = create_experiment()
            excluded = {"b": 0}
            # skip simulations contain tags with {"b":0}
            skip_sims = [sim.id for sim in experiment.simulations if any(sim.tags.get(k) == v for k, v in excluded.items())]
            suite = experiment.suite
            # this returns dict with experiment_id as key and list of simulation as value
            result = suite.simulations_with_tags(tags={"a": 0}, skip_sims=skip_sims, entity_type=True)
            # validation--------------------------------------------
            # make sure each simulation contains tag {"a": 0} and not contains {"b": 0} in returned simulations
            expected = {"a": 0}
            for sim in result[experiment.id]:
                self.assertTrue(isinstance(sim, Simulation))
                # make sure all simulation do not contain tags with {"b": 0}
                assert not all(item in sim.tags.items() for item in excluded.items())
                assert all(item in sim.tags.items() for item in expected.items())
            # make sure we have 4 simulations matched
            self.assertEqual(len(result[experiment.id]), 4)

    def test_experiment_sim_tags_skip_sims(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            platform = Platform('CONTAINER', job_directory=temp_dir)
            sys.path.insert(0, os.path.dirname(__file__))
            experiment = create_experiment()
            # this returns list of simulations
            excluded = {"b": 0}
            # skip simulations contain tags with {"b":0}
            skip_sims = [sim.id for sim in experiment.simulations if
                         any(sim.tags.get(k) == v for k, v in excluded.items())]
            simulations = experiment.simulations_with_tags(tags={"a": 0}, skip_sims=skip_sims, entity_type=True)
            # validation--------------------------------------------
            expected = {"a": 0}
            # make sure each simulation contains tag {"a": 0} and not contains {"b": 0} in returned simulations
            for sim in simulations:
                self.assertTrue(isinstance(sim, Simulation))
                assert not all(item in sim.tags.items() for item in excluded.items())
                assert all(item in sim.tags.items() for item in expected.items())
            # make sure we have 5 simulations matched
            self.assertEqual(len(simulations), 4)