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
        self.assertEqual(len(simulations), len(expected_values))
        # Verify simulations individually
        for simulation, value in zip(simulations, expected_values):
            expected_dict = {"a": value[0], "b": value[1]}
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
        self.assertEqual(builder2.count, len(first) * len(second))
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
        expected_values = list(itertools.product(a, b))
        self.assertEqual(self.builder.count, len(expected_values))
        templated_sim = self.get_templated_sim_builder()
        simulations = list(templated_sim)
        # Test if we have correct number of simulations
        self.assertEqual(len(simulations), len(expected_values))
        # Verify simulations individually
        for simulation, value in zip(simulations, expected_values):
            expected_dict = {"a": value[0], "b": value[1]}
            self.assertEqual(simulation.task.parameters, expected_dict)

    def test_single_dict(self):
        a = {"first": 10}  # test only one dict
        b = [1, 2, 3]
        self.builder.add_sweep_definition(setA, a)
        self.builder.add_sweep_definition(setB, b)
        expected_values = list(itertools.product([a], b))
        self.assertEqual(self.builder.count, len(expected_values))
        templated_sim = self.get_templated_sim_builder()
        simulations = list(templated_sim)
        # Test if we have correct number of simulations
        self.assertEqual(len(simulations), len(expected_values))
        # Verify simulations individually
        for simulation, value in zip(simulations, expected_values):
            expected_dict = {"a": value[0], "b": value[1]}
            self.assertEqual(simulation.task.parameters, expected_dict)

    def test_single_string(self):
        a = "test"  # test string instead of list of string
        b = [1, 2, 3]
        self.builder.add_sweep_definition(setA, a)
        self.builder.add_sweep_definition(setB, b)
        expected_values = list(itertools.product([a], b))
        self.assertEqual(self.builder.count, len(expected_values))
        templated_sim = self.get_templated_sim_builder()
        simulations = list(templated_sim)
        # Test if we have correct number of simulations
        self.assertEqual(len(simulations), len(expected_values))
        # Verify simulations individually
        for simulation, value in zip(simulations, expected_values):
            expected_dict = {"a": value[0], "b": value[1]}
            self.assertEqual(simulation.task.parameters, expected_dict)

    def test_single_list(self):
        a = [10]  # test single item list
        b = [1, 2, 3]
        self.builder.add_sweep_definition(setA, a)
        self.builder.add_sweep_definition(setB, b)
        expected_values = list(itertools.product(a, b))
        self.assertEqual(self.builder.count, len(expected_values))
        templated_sim = self.get_templated_sim_builder()
        simulations = list(templated_sim)
        # Test if we have correct number of simulations
        self.assertEqual(len(simulations), len(expected_values))
        # Verify simulations individually
        for simulation, value in zip(simulations, expected_values):
            expected_dict = {"a": value[0], "b": value[1]}
            self.assertEqual(simulation.task.parameters, expected_dict)

    def test_tuple(self):
        a = (4, 5, 6)
        b = (1, 2, 3)
        self.builder.add_sweep_definition(setA, a)
        self.builder.add_sweep_definition(setB, b)
        expected_values = list(itertools.product(a, b))
        self.assertEqual(self.builder.count, len(expected_values))
        templated_sim = self.get_templated_sim_builder()
        simulations = list(templated_sim)
        # Test if we have correct number of simulations
        self.assertEqual(len(simulations), len(expected_values))
        # Verify simulations individually
        for simulation, value in zip(simulations, expected_values):
            expected_dict = {"a": value[0], "b": value[1]}
            self.assertEqual(simulation.task.parameters, expected_dict)

    def test_add_multiple_parameter_sweep_definition(self):
        a = [True, False]
        b = [1, 2, 3, 4, 5]
        c = ["test"]
        self.builder.add_multiple_parameter_sweep_definition(update_parameter_callback, a, b, c)
        templated_sim = self.get_templated_sim_builder()
        # convert template to a fully realized list
        simulations = list(templated_sim)
        # Test if we have correct number of simulations
        expected_values = list(itertools.product(a, b, c))
        self.assertEqual(len(simulations), len(expected_values))

        # Verify simulations individually
        for simulation, value in zip(simulations, expected_values):
            expected_dict = {"param_a": value[0], "param_b": value[1], "param_c": value[2]}
            self.assertEqual(simulation.task.parameters, expected_dict)

        # test with single string for c instead of list of string as ["test"]
        c = "test"
        builder2 = SimulationBuilder()
        builder2.add_multiple_parameter_sweep_definition(update_parameter_callback, a, b, c)
        templated_sim2 = self.get_templated_sim_builder()
        simulations2 = list(templated_sim2)
        expected_values2 = list(itertools.product(a, b, [c]))
        # Test if we have correct number of simulations
        self.assertEqual(len(simulations2), len(expected_values2))
        # Verify simulations individually
        for simulation, value in zip(simulations2, expected_values2):
            expected_dict = {"param_a": value[0], "param_b": value[1], "param_c": value[2]}
            self.assertEqual(simulation.task.parameters, expected_dict)

    def test_add_multiple_parameter_sweep_definition_dict(self):
        test_dict = {"a": [True, False], "b": [1, 2, 3, 4, 5], "c": ["test"]}
        # a = [True, False]
        # b = [1, 2, 3, 4, 5]
        # c = ["test"]
        self.builder.add_multiple_parameter_sweep_definition(update_parameter_callback, test_dict)
        templated_sim = self.get_templated_sim_builder()
        # convert template to a fully realized list
        simulations = list(templated_sim)
        # Test if we have correct number of simulations
        expected_values = list(itertools.product(test_dict['a'], test_dict['b'], test_dict['c']))
        self.assertEqual(len(simulations), len(expected_values))

        # Verify simulations individually
        for simulation, value in zip(simulations, expected_values):
            expected_dict = {"param_a": value[0], "param_b": value[1], "param_c": value[2]}
            self.assertEqual(simulation.task.parameters, expected_dict)

        # test with single string for c instead of list of string as ["test"]
        test_dict2 = {"a": [True, False], "b": [1, 2, 3, 4, 5], "c": "test"}
        builder2 = SimulationBuilder()
        builder2.add_multiple_parameter_sweep_definition(update_parameter_callback, test_dict2)
        templated_sim2 = self.get_templated_sim_builder()
        simulations2 = list(templated_sim2)
        expected_values2 = list(itertools.product(test_dict2['a'], test_dict2['b'], [test_dict2['c']]))
        # Test if we have correct number of simulations
        self.assertEqual(len(simulations2), len(expected_values2))
        # Verify simulations individually
        for simulation, value in zip(simulations2, expected_values2):
            expected_dict = {"param_a": value[0], "param_b": value[1], "param_c": value[2]}
            self.assertEqual(simulation.task.parameters, expected_dict)
