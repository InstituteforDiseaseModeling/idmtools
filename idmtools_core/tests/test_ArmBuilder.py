import itertools
from functools import partial
from idmtools.builders.arm_simulation_builder import ArmSimulationBuilder, SweepArm, ArmType
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools_test.utils.test_task import TestTask
from idmtools_test.utils.utils import verify_simulation


def param_update(simulation, param, value):
    return simulation.task.set_parameter(param, value)


setA = partial(param_update, param="a")
setB = partial(param_update, param="b")


class TestArmBuilder(ITestWithPersistence):

    def setUp(self):
        super().setUp()
        self.builder = ArmSimulationBuilder()

    def tearDown(self):
        super().tearDown()

    def test_simple_arm_cross(self):
        self.create_simple_arm()

        expected_values = list(itertools.product(range(5), [1, 2, 3]))
        templated_sim = self.get_templated_sim_builder()

        # convert template to a fully realized list
        simulations = list(templated_sim)

        # Test if we have correct number of simulations
        self.assertEqual(len(simulations), 15)

        # Verify simulations individually
        for simulation in simulations:
            found = verify_simulation(simulation, ["a", "b"], expected_values)
            self.assertTrue(found)

    def get_templated_sim_builder(self):
        templated_sim = TemplatedSimulations(base_task=TestTask())
        templated_sim.builder = self.builder
        return templated_sim

    def create_simple_arm(self):
        arm = SweepArm(type=ArmType.cross)
        arm.add_sweep_definition(setA, range(5))
        arm.add_sweep_definition(setB, [1, 2, 3])
        self.builder.add_arm(arm)

    def test_reverse_order(self):
        self.create_simple_arm()

        templated_sim = self.get_templated_sim_builder()

        # convert template to a fully realized list
        simulations_cfgs = list([s.task.parameters for s in templated_sim])

        builder2 = ArmSimulationBuilder()

        arm = SweepArm(type=ArmType.cross)
        arm.add_sweep_definition(setB, [1, 2, 3])
        arm.add_sweep_definition(setA, range(5))
        builder2.add_arm(arm)

        # convert template to a fully realized list
        templated_sim2 = TemplatedSimulations(base_task=TestTask())
        templated_sim2.builder = builder2

        simulations2_cfgs = list([s.task.parameters for s in templated_sim2])

        for cfg in simulations_cfgs:
            self.assertIn(dict(b=cfg['b'], a=cfg['a']), simulations2_cfgs)

    def test_simple_arm_pair(self):
        arm = SweepArm(type=ArmType.pair)
        arm.add_sweep_definition(setA, range(5))
        arm.add_sweep_definition(setB, [1, 2, 3])
        self.builder.add_arm(arm)

        expected_values = list(zip(range(5), [1, 2, 3]))

        templated_sim = self.get_templated_sim_builder()

        # convert template to a fully realized list
        simulations = list(templated_sim)

        # Test if we have correct number of simulations
        self.assertEqual(len(simulations), 5)

        # Verify simulations individually
        for simulation in simulations:
            found = verify_simulation(simulation, ["a", "b"], expected_values)
            self.assertTrue(found)

    def test_complex_scenario(self):
        pass
