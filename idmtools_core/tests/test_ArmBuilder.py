import itertools
from functools import partial

from idmtools.builders.arm_experiment_builder import ArmExperimentBuilder, SweepArm, ArmType
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools_test.utils.tst_experiment import TstExperiment
from idmtools_test.utils.utils import verify_simulation


def param_update(simulation, param, value):
    return simulation.set_parameter(param, value)


setA = partial(param_update, param="a")
setB = partial(param_update, param="b")


class TestArmBuilder(ITestWithPersistence):

    def setUp(self):
        super().setUp()
        self.builder = ArmExperimentBuilder()

    def tearDown(self):
        super().tearDown()

    def test_simple_arm_cross(self):
        self.create_simple_arm()

        expected_values = list(itertools.product(range(5), [1, 2, 3]))

        experiment = TstExperiment("test")
        experiment.builder = self.builder

        simulations = list(experiment.batch_simulations(20))[0]

        # Test if we have correct number of simulations
        self.assertEqual(len(simulations), 15)

        # Verify simulations individually
        for simulation in simulations:
            found = verify_simulation(simulation, ["a", "b"], expected_values)
            self.assertTrue(found)

    def create_simple_arm(self):
        arm = SweepArm(type=ArmType.cross)
        arm.add_sweep_definition(setA, range(5))
        arm.add_sweep_definition(setB, [1, 2, 3])
        self.builder.add_arm(arm)

    def test_reverse_order(self):
        self.create_simple_arm()

        experiment = TstExperiment("test")
        experiment.builder = self.builder

        simulations = list(experiment.batch_simulations(20))[0]

        builder2 = ArmExperimentBuilder()

        arm = SweepArm(type=ArmType.cross)
        arm.add_sweep_definition(setB, [1, 2, 3])
        arm.add_sweep_definition(setA, range(5))
        builder2.add_arm(arm)

        experiment2 = TstExperiment("test")
        experiment2.builder = self.builder

        simulations2 = list(experiment.batch_simulations(20))[0]

        self.assertListEqual(simulations2, simulations)

    def test_simple_arm_pair(self):
        arm = SweepArm(type=ArmType.pair)
        arm.add_sweep_definition(setA, range(5))
        arm.add_sweep_definition(setB, [1, 2, 3])
        self.builder.add_arm(arm)

        expected_values = list(zip(range(5), [1, 2, 3]))

        experiment = TstExperiment("test")
        experiment.builder = self.builder

        simulations = list(experiment.batch_simulations(10))[0]

        # Test if we have correct number of simulations
        self.assertEqual(len(simulations), 5)

        # Verify simulations individually
        for simulation in simulations:
            found = verify_simulation(simulation, ["a", "b"], expected_values)
            self.assertTrue(found)

    def test_complex_scenario(self):
        pass
