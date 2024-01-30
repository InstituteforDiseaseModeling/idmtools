import allure
import itertools
from functools import partial

import pytest
from idmtools.builders.arm_simulation_builder import ArmSimulationBuilder, SweepArm, ArmType
from idmtools.entities.simulation import Simulation
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools_test.utils.test_task import TestTask
from idmtools_test.utils.utils import verify_simulation


class TestTestTask(TestTask):
    @staticmethod
    def set_parameter_sweep_callback(simulation: Simulation, param: str, value):
        if not hasattr(simulation.task, 'set_parameter'):
            raise ValueError("update_task_with_set_parameter can only be used on tasks with a set_parameter")
        return simulation.task.set_parameter(param, value)

    @classmethod
    def set_parameter_partial(cls, parameter: str):
        return partial(cls.set_parameter_sweep_callback, param=parameter)


setA = partial(TestTestTask.set_parameter_sweep_callback, param="a")
setB = partial(TestTestTask.set_parameter_sweep_callback, param="b")


@pytest.mark.smoke
@allure.story("Sweeps")
@allure.suite("idmtools_core")
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
