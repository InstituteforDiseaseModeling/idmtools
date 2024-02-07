import allure
import itertools
from functools import partial

import pytest

from idmtools.builders import SimulationBuilder
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.json_configured_task import JSONConfiguredTask
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools_test.utils.test_task import TestTask

setA = partial(JSONConfiguredTask.set_parameter_sweep_callback, param="a")
setB = partial(JSONConfiguredTask.set_parameter_sweep_callback, param="b")


def update_parameter_callback(simulation, a, b, c):
    simulation.task.set_parameter("param_a", a)
    simulation.task.set_parameter("param_b", b)
    simulation.task.set_parameter("param_c", c)
    return {"a": a, "b": b, "c": c}


@pytest.mark.smoke
@allure.story("Sweeps")
@allure.suite("idmtools_core")
class TestArmBuilder(ITestWithPersistence):

    def setUp(self):
        super().setUp()
        self.builder = SimulationBuilder()

    def tearDown(self):
        super().tearDown()

    def get_templated_sim_builder(self):
        templated_sim = TemplatedSimulations(base_task=TestTask())
        templated_sim.builder = self.builder
        return templated_sim

    def create_simple_sweep(self):
        self.builder.add_sweep_definition(setA, range(5))
        self.builder.add_sweep_definition(setB, [1, 2, 3])

    def test_simple_simulation_builder(self):
        self.create_simple_sweep()
        expected_values = list(itertools.product(range(5), [1, 2, 3]))
        templated_sim = self.get_templated_sim_builder()
        # convert template to a fully realized list
        simulations = list(templated_sim)

        # Test if we have correct number of simulations
        self.assertEqual(len(simulations), 15)

        # Verify simulations individually
        for i, simulation in enumerate(simulations):
            expected_dict = {"a": expected_values[i][0], "b": expected_values[i][1]}
            self.assertEqual(simulation.task.parameters, expected_dict)

    def test_reverse_order(self):
        self.create_simple_sweep()

        templated_sim = self.get_templated_sim_builder()

        # convert template to a fully realized list
        simulations_cfgs = list([s.task.parameters for s in templated_sim])

        # reverse
        builder2 = SimulationBuilder()
        first = [1, 2, 3]
        second = range(5)
        builder2.add_sweep_definition(setB, first)
        builder2.add_sweep_definition(setA, second)
        self.assertEqual(builder2.count, first.__len__() * second.__len__())
        templated_sim2 = TemplatedSimulations(base_task=TestTask())
        templated_sim2.builder = builder2

        simulations2_cfgs = list([s.task.parameters for s in templated_sim2])

        for cfg in simulations_cfgs:
            self.assertIn(dict(b=cfg['b'], a=cfg['a']), simulations2_cfgs)

    def test_single_item_simulation_builder(self):
        a = 10  # test only one item not list
        self.builder.add_sweep_definition(setA, a)
        self.assertEqual(self.builder.count, 1)

    def test_dict_list(self):
        a = [{"first": 10}, {"second": 20}]
        b = [1, 2, 3]
        self.builder.add_sweep_definition(setA, a)
        self.builder.add_sweep_definition(setB, b)
        self.assertEqual(self.builder.count, 6)
        templated_sim = self.get_templated_sim_builder()
        simulations = list(templated_sim)
        # Test if we have correct number of simulations
        self.assertEqual(len(simulations), 6)

        expected_values = [{'a': {'first': 10}, 'b': 1},
                           {'a': {'first': 10}, 'b': 2},
                           {'a': {'first': 10}, 'b': 3},
                           {'a': {'second': 20}, 'b': 1},
                           {'a': {'second': 20}, 'b': 2},
                           {'a': {'second': 20}, 'b': 3}
                           ]
        # Verify simulations individually
        for i, simulation in enumerate(simulations):
            self.assertEqual(simulation.task.parameters, expected_values[i])

    def test_single_dict(self):
        a = {"first": 10}  # test only one dict
        b = [1, 2, 3]
        self.builder.add_sweep_definition(setA, a)
        self.builder.add_sweep_definition(setB, b)
        self.assertEqual(self.builder.count, 3)
        templated_sim = self.get_templated_sim_builder()
        simulations = list(templated_sim)
        # Test if we have correct number of simulations
        self.assertEqual(len(simulations), 3)
        expected_values = [{'a': {'first': 10}, 'b': 1},
                           {'a': {'first': 10}, 'b': 2},
                           {'a': {'first': 10}, 'b': 3}
                           ]
        # Verify simulations individually
        for i, simulation in enumerate(simulations):
            self.assertEqual(simulation.task.parameters, expected_values[i])

    def test_single_string(self):
        a = "test"  # test string instead of list of string
        b = [1, 2, 3]
        self.builder.add_sweep_definition(setA, a)
        self.builder.add_sweep_definition(setB, b)
        self.assertEqual(self.builder.count, 3)
        templated_sim = self.get_templated_sim_builder()
        # convert template to a fully realized list
        simulations = list(templated_sim)
        # Test if we have correct number of simulations
        self.assertEqual(len(simulations), 3)
        expected_values = [{'a': 'test', 'b': 1},
                           {'a': 'test', 'b': 2},
                           {'a': 'test', 'b': 3}
                           ]
        # Verify simulations individually
        for i, simulation in enumerate(simulations):
            self.assertEqual(simulation.task.parameters, expected_values[i])

    def test_single_list(self):
        a = [10]  # test single item list
        b = [1, 2, 3]
        self.builder.add_sweep_definition(setA, a)
        self.builder.add_sweep_definition(setB, b)
        self.assertEqual(self.builder.count, 3)
        templated_sim = self.get_templated_sim_builder()
        simulations = list(templated_sim)
        # Test if we have correct number of simulations
        self.assertEqual(len(simulations), 3)
        expected_values = [{'a': 10, 'b': 1},
                           {'a': 10, 'b': 2},
                           {'a': 10, 'b': 3}
                           ]
        # Verify simulations individually
        for i, simulation in enumerate(simulations):
            self.assertEqual(simulation.task.parameters, expected_values[i])

    def test_tuple(self):
        a = (4, 5, 6)
        b = (1, 2, 3)
        self.builder.add_sweep_definition(setA, a)
        self.builder.add_sweep_definition(setB, b)
        self.assertEqual(self.builder.count, 9)
        templated_sim = self.get_templated_sim_builder()
        simulations = list(templated_sim)
        # Test if we have correct number of simulations
        self.assertEqual(len(simulations), 9)
        expected_values = [{'a': 4, 'b': 1},
                           {'a': 4, 'b': 2},
                           {'a': 4, 'b': 3},
                           {'a': 5, 'b': 1},
                           {'a': 5, 'b': 2},
                           {'a': 5, 'b': 3},
                           {'a': 6, 'b': 1},
                           {'a': 6, 'b': 2},
                           {'a': 6, 'b': 3}
                           ]
        # Verify simulations individually
        for i, simulation in enumerate(simulations):
            self.assertEqual(simulation.task.parameters, expected_values[i])

    def test_add_multiple_parameter_sweep_definition(self):
        a = [True, False]
        b = [1, 2, 3, 4, 5]
        c = ["test"]
        self.builder.add_multiple_parameter_sweep_definition(update_parameter_callback, a, b, c)
        templated_sim = self.get_templated_sim_builder()
        # convert template to a fully realized list
        simulations = list(templated_sim)
        # Test if we have correct number of simulations
        self.assertEqual(len(simulations), 10)
        expected_values = list(itertools.product(a, b, c))
        for i, simulation in enumerate(simulations):
            expected_parameter = {"param_a": expected_values[i][0], "param_b": expected_values[i][1],
                                  "param_c": expected_values[i][2]}
            self.assertEqual(simulation.task.parameters, expected_parameter)

        # test with single string for c instead of list of string as ["test"]
        c = "test"
        builder2 = SimulationBuilder()
        builder2.add_multiple_parameter_sweep_definition(update_parameter_callback, a, b, c)
        templated_sim2 = self.get_templated_sim_builder()
        simulations2 = list(templated_sim2)
        # Test if we have correct number of simulations
        self.assertEqual(len(simulations2), 10)
        for i, simulation in enumerate(simulations2):
            expected_parameter = {"param_a": expected_values[i][0], "param_b": expected_values[i][1],
                                  "param_c": expected_values[i][2]}
            self.assertEqual(simulation.task.parameters, expected_parameter)
