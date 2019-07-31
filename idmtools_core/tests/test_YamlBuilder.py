import os
from functools import partial
from idmtools.builders.ArmExperimentBuilder import ArmType
from idmtools.builders.YamlExperimentBuilder import YamlExperimentBuilder
from idmtools_test.utils.ITestWithPersistence import ITestWithPersistence
from idmtools_test.utils.TestExperiment import TestExperiment
from idmtools_test import COMMON_INPUT_PATH


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


class TestArmBuilder(ITestWithPersistence):

    def setUp(self):
        super().setUp()
        self.builder = YamlExperimentBuilder()
        self.base_path = os.path.abspath(os.path.join(COMMON_INPUT_PATH, "builder"))

    def tearDown(self):
        super().tearDown()

    def test_simple_yaml_cross(self):
        file_path = os.path.join(self.base_path, 'sweeps.yaml')
        func_map = {'a': setA, 'b': setB, 'c': setC, 'd': setD}
        self.builder.add_sweeps_from_file(file_path, func_map)

        # expected_values = list(itertools.product(range(5), [1, 2, 3]))

        experiment = TestExperiment("test")
        experiment.builder = self.builder

        simulations = list(experiment.batch_simulations(20))[0]

        # Test if we have correct number of simulations
        self.assertEqual(len(simulations), 10)

        # Verify simulations individually
        # for simulation in simulations:
        #     found = verify_simulation(simulation, ["a", "b"], expected_values)
        #     self.assertTrue(found)

    def test_simple_yaml_zip(self):
        file_path = os.path.join(self.base_path, 'sweeps.yaml')
        func_map = {'a': setA, 'b': setB, 'c': setC, 'd': setD}
        self.builder.add_sweeps_from_file(file_path, func_map, sweep_type=ArmType.pair)

        # expected_values = list(itertools.product(range(5), [1, 2, 3]))

        experiment = TestExperiment("test")
        experiment.builder = self.builder

        simulations = list(experiment.batch_simulations(10))[0]

        for s in simulations:
            print(s._uid, ": ", s.parameters)

        # Test if we have correct number of simulations
        self.assertEqual(len(simulations), 5)

        # Verify simulations individually
        # for simulation in simulations:
        #     found = verify_simulation(simulation, ["a", "b"], expected_values)
        #     self.assertTrue(found)

    def test_complex_scenario(self):
        pass
