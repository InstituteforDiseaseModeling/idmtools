import allure
import itertools
from functools import partial

import pytest
from idmtools.builders.arm_simulation_builder import ArmSimulationBuilder, SweepArm, ArmType
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.json_configured_task import JSONConfiguredTask
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools_test.utils.test_task import TestTask

setA = partial(JSONConfiguredTask.set_parameter_sweep_callback, param="a")
setB = partial(JSONConfiguredTask.set_parameter_sweep_callback, param="b")


def update_parameter_callback(simulation, a, b, c):
    simulation.task.command.add_argument(a)
    simulation.task.command.add_argument(b)
    simulation.task.command.add_argument(c)
    return {"a": a, "b": b, "c": c}


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
        for simulation, value in zip(simulations, expected_values):
            expected_dict = {"a": value[0], "b": value[1]}
            self.assertEqual(simulation.task.parameters, expected_dict)

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
        a = [1, 2, 3]
        b = range(5)
        arm.add_sweep_definition(setB, a)
        arm.add_sweep_definition(setA, b)
        builder2.add_arm(arm)
        self.assertEqual(builder2.count, len(a) * len(b))

        # convert template to a fully realized list
        templated_sim2 = TemplatedSimulations(base_task=TestTask())
        templated_sim2.builder = builder2

        simulations2_cfgs = list([s.task.parameters for s in templated_sim2])

        for cfg in simulations_cfgs:
            self.assertIn(dict(b=cfg['b'], a=cfg['a']), simulations2_cfgs)

    def test_simple_arm_pair_uneven_pairs(self):
        with self.assertRaises(ValueError) as ex:
            arm = SweepArm(type=ArmType.pair)
            a = range(5)
            b = [1, 2, 3]
            arm.add_sweep_definition(setA, a)
            arm.add_sweep_definition(setB, b)  # Adding different length of list, expect throw exception
            self.builder.add_arm(arm)
        self.assertEqual(ex.exception.args[0],
                         f"For pair case, all function inputs must have the save size/length: {len(b)} != {len(a)}")

    def test_simple_arm_pair(self):
        arm = SweepArm(type=ArmType.pair)
        a = range(5)
        # Add same length pair
        b = [1, 2, 3, 4, 5]
        arm.add_sweep_definition(setA, a)
        arm.add_sweep_definition(setB, b)
        self.builder.add_arm(arm)
        self.assertEqual(self.builder.count, len(a))

        expected_values = list(zip(a, b))

        templated_sim = self.get_templated_sim_builder()
        simulations = list(templated_sim)
        # Test if we have correct number of simulations
        self.assertEqual(len(simulations), len(a))

        # Verify simulations individually
        for i, simulation in enumerate(simulations):
            expected_dict = {"a": expected_values[i][0], "b": expected_values[i][1]}
            self.assertEqual(simulation.task.parameters, expected_dict)

    def test_add_multiple_parameter_sweep_definition_via_builder(self):
        a = [True, False]
        b = [1, 2, 3, 4, 5]
        c = "test"
        with self.assertRaises(ValueError) as ex:
            self.builder.add_multiple_parameter_sweep_definition(update_parameter_callback, a, b, c)
        self.assertEqual(ex.exception.args[0], "Please use SweepArm instead, or use SimulationBuilder directly!")

    def test_add_multiple_parameter_sweep_definition(self):
        arm = SweepArm()
        a = [True, False]
        b = [1, 2, 3, 4, 5]
        c = "test"
        arm.add_multiple_parameter_sweep_definition(update_parameter_callback, a, b, c)
        d = (6, 7)
        setD = partial(JSONConfiguredTask.set_parameter_sweep_callback, param="d")
        arm.add_sweep_definition(setD, d)
        self.builder.add_arm(arm)
        self.assertEqual(self.builder.count, len(a) * len(b) * len([c]) * len(d))

        # case2: add 2 multiple_parameter_definitions
        self.builder = ArmSimulationBuilder()
        arm2 = SweepArm()
        arm2.add_multiple_parameter_sweep_definition(update_parameter_callback, a, b, c)
        arm2.add_multiple_parameter_sweep_definition(update_parameter_callback, a, b, c)
        self.builder.add_arm(arm2)
        self.assertEqual(self.builder.count, (len(a) * len(b) * len([c])) * (len(a) * len(b) * len([c])))

    def test_add_multiple_parameter_sweep_definition_pair(self):
        a = [True, False]
        b = [1, 2, 3, 4, 5]
        c = "test"
        with self.subTest("test_multiple_single_parameter_pair"):
            arm = SweepArm(type=ArmType.pair)
            arm.add_multiple_parameter_sweep_definition(update_parameter_callback, a, b, c)
            self.assertEqual(arm.count, len(a) * len(b) * len([c]))
            d = range(10)
            setD = partial(JSONConfiguredTask.set_parameter_sweep_callback, param="d")
            arm.add_sweep_definition(setD, d)
            self.builder.add_arm(arm)
            self.assertEqual(self.builder.count, len(d))  # for pair, count equals each arm's count

        # case2: add 2 multiple_parameter_definitions
        with self.subTest("test_multiple_multiple_parameter_pair"):
            self.builder = ArmSimulationBuilder()
            arm2 = SweepArm(type=ArmType.pair)
            arm2.add_multiple_parameter_sweep_definition(update_parameter_callback, a, b, c)
            arm2.add_multiple_parameter_sweep_definition(update_parameter_callback, a, b, c)
            self.builder.add_arm(arm2)
            self.assertEqual(self.builder.count, (len(a) * len(b) * len([c])))

        # case3: two pairs not match with length
        with self.subTest("test_mismatch_length_pair"):
            self.builder = ArmSimulationBuilder()
            arm3 = SweepArm(type=ArmType.pair)
            arm3.add_multiple_parameter_sweep_definition(update_parameter_callback, a, b, c)
            e = [1,2,3]
            setE = partial(JSONConfiguredTask.set_parameter_sweep_callback, param="e")
            with self.assertRaises(ValueError) as ex:
                arm3.add_sweep_definition(setE, e)
            self.assertEqual(ex.exception.args[0],
                             f"For pair case, all function inputs must have the save size/length: {len(e)} != {len(a) * len(b) * len([c])}")

    def test_single_item_arm_builder(self):
        arm = SweepArm()
        a = 10  # test only one item not list
        b = [1, 2, 3, 4, 5]
        arm.add_sweep_definition(setA, a)
        arm.add_sweep_definition(setB, b)
        self.builder.add_arm(arm)
        self.assertEqual(self.builder.count, len([a]) * len(b))

    def test_dict_arm_builder(self):
        arm = SweepArm()
        a = [{"first": 10}, {"second": 20}]
        b = [1, 2, 3]
        expected_values = list(itertools.product(a, b))
        arm.add_sweep_definition(setA, a)
        arm.add_sweep_definition(setB, b)
        self.builder.add_arm(arm)
        self.assertEqual(self.builder.count, len(expected_values))
        templated_sim = self.get_templated_sim_builder()
        simulations = list(templated_sim)
        # Test if we have correct number of simulations
        self.assertEqual(len(simulations), len(expected_values))
        # Verify simulations individually
        for simulation, value in zip(simulations, expected_values):
            expected_dict = {"a": value[0], "b": value[1]}
            self.assertEqual(simulation.task.parameters, expected_dict)

    def test_single_item_arm_builder(self):
        arm = SweepArm()
        a = 10  # test only one item not list
        b = [1, 2, 3, 4, 5]
        arm.add_sweep_definition(setA, a)
        arm.add_sweep_definition(setB, b)
        self.builder.add_arm(arm)
        self.assertEqual(self.builder.count, len([a]) * len(b))

    def test_single_dict_arm_builder(self):
        arm = SweepArm()
        a = {"a": 10}  # test only one dict. we actually sweep on dict value
        b = [1, 2, 3]

        def sweep_function_a(simulation, a):
            simulation.task.set_parameter("param_a", a)
            return {"param_a": a}

        def sweep_function_b(simulation, b):
            simulation.task.set_parameter("param_b", b)
            return {"param_ab": a}

        arm.add_sweep_definition(sweep_function_a, a)
        arm.add_sweep_definition(sweep_function_b, b)
        self.builder.add_arm(arm)
        expected_values = list(itertools.product([a['a']], b))
        self.assertEqual(self.builder.count, len(expected_values))
        templated_sim = self.get_templated_sim_builder()
        simulations = list(templated_sim)
        # Test if we have correct number of simulations
        self.assertEqual(len(simulations), len(expected_values))
        # Verify simulations individually
        for simulation, value in zip(simulations, expected_values):
            expected_dict = {"param_a": value[0], "param_b": value[1]}
            self.assertEqual(simulation.task.parameters, expected_dict)

    def test_single_string_arm_builder(self):
        arm = SweepArm()
        a = "test"  # test only 1 string
        b = [1, 2, 3]
        arm.add_sweep_definition(setA, a)
        arm.add_sweep_definition(setB, b)
        self.builder.add_arm(arm)
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

    def test_single_list_arm_builder(self):
        arm = SweepArm()
        a = [10]  # test only one item in list
        b = [1, 2, 3]
        arm.add_sweep_definition(setA, a)
        arm.add_sweep_definition(setB, b)
        self.builder.add_arm(arm)
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

    def test_tuple_arm_builder(self):
        arm = SweepArm()
        a = (4, 5, 6)  # test tuple
        b = [1, 2, 3]
        arm.add_sweep_definition(setA, a)
        arm.add_sweep_definition(setB, b)
        self.builder.add_arm(arm)
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
