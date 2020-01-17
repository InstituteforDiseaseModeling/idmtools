import os
from functools import partial
from idmtools.builders.arm_experiment_builder import ArmType
from idmtools.builders.yaml_experiment_builder import YamlExperimentBuilder
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools_test.utils.tst_experiment import TstExperiment
from idmtools_test import COMMON_INPUT_PATH


def param_update(simulation, param, value):
    return simulation.set_parameter(param, value)


setA = partial(param_update, param="a")
setB = partial(param_update, param="b")
setC = partial(param_update, param="c")
setD = partial(param_update, param="d")


class TestYamlBuilder(ITestWithPersistence):

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

        experiment = TstExperiment("test")
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

        experiment = TstExperiment("test")
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
