import os
import numpy as np
from functools import partial
from idmtools.builders import CsvExperimentBuilder
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.ITestWithPersistence import ITestWithPersistence
from idmtools_test.utils.TestExperiment import TestExperiment


def param_update(simulation, param, value):
    return simulation.set_parameter(param, value)


setA = partial(param_update, param="a")
setB = partial(param_update, param="b")
setC = partial(param_update, param="c")
setD = partial(param_update, param="d")


def verify_simulation(simulation, expected_parameters, expected_values):
    for value_set in expected_values:
        for i, value in enumerate(list(value_set)):
            if not simulation.parameters[expected_parameters[i]] == expected_values:
                break
        return True
    return False


class TestCsvBuilder(ITestWithPersistence):

    def setUp(self):
        super().setUp()
        self.builder = CsvExperimentBuilder()
        self.base_path = os.path.abspath(os.path.join(COMMON_INPUT_PATH, "builder"))

    def tearDown(self):
        super().tearDown()

    def test_simple_csv(self):
        file_path = os.path.join(self.base_path, 'sweeps.csv')
        func_map = {'a': setA, 'b': setB, 'c': setC, 'd': setD}
        type_map = {'a': np.int, 'b': np.int, 'c': np.int, 'd': np.int}
        self.builder.add_sweeps_from_file(file_path, func_map, type_map)

        # expected_values = list(itertools.product(range(5), [1, 2, 3]))

        experiment = TestExperiment("test")
        experiment.builder = self.builder

        simulations = list(experiment.batch_simulations(10))[0]

        # Test if we have correct number of simulations
        self.assertEqual(len(simulations), 5)

        # Verify simulations individually
        # for simulation in simulations:
        #     found = verify_simulation(simulation, ["a", "b"], expected_values)
        #     self.assertTrue(found)

    def test_complex_scenario(self):
        pass
