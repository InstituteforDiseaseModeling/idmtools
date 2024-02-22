import allure
import os
from functools import partial

import pytest
from idmtools.builders.yaml_simulation_builder import YamlSimulationBuilder
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools_test.utils.test_task import TestTask


def param_update(simulation, param, value):
    return simulation.task.set_parameter(param, value)


setA = partial(param_update, param="a")
setB = partial(param_update, param="b")
setC = partial(param_update, param="c")
setD = partial(param_update, param="d")


@pytest.mark.smoke
@allure.story("Sweeps")
@allure.suite("idmtools_core")
class TestYamlBuilder(ITestWithPersistence):

    def setUp(self):
        super().setUp()
        self.builder = YamlSimulationBuilder()
        self.base_path = os.path.abspath(os.path.join(COMMON_INPUT_PATH, "builder"))

    def tearDown(self):
        super().tearDown()

    def get_templated_sim_builder(self):
        templated_sim = TemplatedSimulations(base_task=TestTask())
        templated_sim.builder = self.builder
        return templated_sim

    def test_simple_yaml(self):
        file_path = os.path.join(self.base_path, 'sweeps.yaml')
        func_map = {'a': setA, 'b': setB, 'c': setC, 'd': setD}
        self.builder.add_sweeps_from_file(file_path, func_map)
        self.assertEqual(self.builder.count, 10)

        templated_sim = self.get_templated_sim_builder()
        simulations = list(templated_sim)

        self.assertEqual(len(simulations), 10)
        expected_values = [{'a': 1, 'b': 2, 'c': 3, 'd': 5},  # group1
                           {'a': 1, 'b': 2, 'c': 3, 'd': 6},  # group1
                           {'a': 1, 'b': 2, 'c': 4, 'd': 5},  # group1
                           {'a': 1, 'b': 2, 'c': 4, 'd': 6},  # group1
                           {'c': 3, 'd': 5},  # group2
                           {'c': 3, 'd': 6},  # group2
                           {'c': 3, 'd': 7},  # group2
                           {'c': 4, 'd': 5},  # group2
                           {'c': 4, 'd': 6},  # group2
                           {'c': 4, 'd': 7}]  # group2

        # Verify simulations individually
        for i, simulation in enumerate(simulations):
            self.assertEqual(simulation.task.parameters, expected_values[i])

