import allure
import os
from functools import partial

import numpy as np
import pytest

from idmtools.builders import ArmSimulationBuilder, SweepArm, ArmType, SimulationBuilder
from idmtools.builders import CsvExperimentBuilder
from idmtools.builders import YamlSimulationBuilder
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools_test.utils.test_task import TestTask


def param_update(simulation, param, value):
    return simulation.task.set_parameter(param, value)


def update_command_task(simulation, a, b):
    simulation.task.config["a"] = a
    simulation.task.config["b"] = b
    return {"a": a, "b": b}


setA = partial(param_update, param="a")
setB = partial(param_update, param="b")
setC = partial(param_update, param="c")
setD = partial(param_update, param="d")


@pytest.mark.smoke
@allure.story("Sweeps")
@allure.suite("idmtools_core")
class TestMultipleBuilders(ITestWithPersistence):

    def setUp(self):
        super().setUp()
        self.base_path = os.path.abspath(os.path.join(COMMON_INPUT_PATH, "builder"))
        self.arm_builder = ArmSimulationBuilder()
        self.yaml_builder = YamlSimulationBuilder()
        self.csv_builder = CsvExperimentBuilder()

    def tearDown(self):
        super().tearDown()

    def test_simple_builders(self):
        # create YamlExperimentBuilder
        file_path = os.path.join(self.base_path, 'sweeps.yaml')
        func_map = {'a': setA, 'b': setB, 'c': setC, 'd': setD}
        self.yaml_builder.add_sweeps_from_file(file_path, func_map)

        # create CsvExperimentBuilder
        file_path = os.path.join(self.base_path, 'sweeps.csv')
        func_map = {'a': setA, 'b': setB, 'c': setC, 'd': setD}
        type_map = {'a': np.int, 'b': np.int, 'c': np.int, 'd': np.int}
        self.csv_builder.add_sweeps_from_file(file_path, func_map, type_map)

        # create ArmExperimentBuilder
        arm = SweepArm(type=ArmType.cross)
        arm.add_sweep_definition(setA, range(2))
        arm.add_sweep_definition(setB, [1, 2, 3])
        self.arm_builder.add_arm(arm)

        # add individual builders
        template_sim = TemplatedSimulations(base_task=TestTask())
        template_sim.add_builder(self.yaml_builder)
        template_sim.add_builder(self.csv_builder)
        template_sim.add_builder(self.arm_builder)

        simulations = list(template_sim)

        # test if we have correct number of simulations
        self.assertEqual(len(simulations), 10 + 5 + 6)

    def test_simulation_builder(self):
        """Test basic simulation builder.

        We also validates the full product exists after creation
        """

        def update_command_task_wrapper(key):
            def update_command_task_a(simulation, value):
                simulation.task.config[key] = value
                return {key: value}

            return update_command_task_a

        sb = SimulationBuilder()
        a_values = range(1, 5)
        sb.add_sweep_definition(update_command_task_wrapper("a"), a_values)
        b_values = ["c", "d"]
        sb.add_sweep_definition(update_command_task_wrapper("b"), b_values)

        self.__validate_a_b_sb_test(a_values, b_values, sb)

    def test_simulation_builder_args(self):
        """Test simulation builder using multiple arguments

        The interesting part of this test is the call to add_multiple_parameter_sweep_definition, otherwise it is an alternate to test_simulation_builder
        """
        sb = SimulationBuilder()
        a_values = range(1, 5)
        b_values = ["c", "d"]
        sb.add_multiple_parameter_sweep_definition(update_command_task, a_values, b_values)

        self.__validate_a_b_sb_test(a_values, b_values, sb)

    def test_simulation_builder_args_single_dict(self):

        sb = SimulationBuilder()
        a_values = range(1, 5)
        b_values = ["c", "d"]
        sb.add_multiple_parameter_sweep_definition(update_command_task, dict(a=a_values, b=b_values))
        self.__validate_a_b_sb_test(a_values, b_values, sb)

    def test_simulation_builder_kwargs(self):
        """Test simulation builder using kwargs"""
        sb = SimulationBuilder()
        a_values = range(1, 5)
        b_values = ["c", "d"]
        sb.add_multiple_parameter_sweep_definition(update_command_task, **dict(a=a_values, b=b_values))
        self.__validate_a_b_sb_test(a_values, b_values, sb)

    def __validate_a_b_sb_test(self, a_values, b_values, sb):
        tt = TestTask()
        tt.config = dict()
        template_sim = TemplatedSimulations(base_task=tt)
        template_sim.add_builder(sb)
        simulations = list(template_sim)
        # test if we have correct number of simulations
        self.assertEqual(len(simulations), len(a_values) * len(b_values))
        for a_value in a_values:
            for b_value in b_values:
                found = False
                for simulation in simulations:
                    if simulation.task.config['a'] == a_value and simulation.task.config['b'] == b_value:
                        found = True
                        break
                self.assertTrue(found, msg=f'Could not find sweep pair of {a_value} and {b_value}')

    def test_duplicates(self):
        arm = SweepArm(type=ArmType.cross)
        arm.add_sweep_definition(setA, range(2))
        arm.add_sweep_definition(setB, [1, 2, 3])
        self.arm_builder.add_arm(arm)

        # add individual builders
        template_sim = TemplatedSimulations(base_task=TestTask())
        template_sim.add_builder(self.arm_builder)
        template_sim.add_builder(self.arm_builder)

        # test if we have correct number of builders
        self.assertEqual(len(template_sim.builders), 1)

    def test_builder_property(self):
        arm = SweepArm(type=ArmType.cross)
        arm.add_sweep_definition(setA, range(2))
        arm.add_sweep_definition(setB, [1, 2, 3])
        self.arm_builder.add_arm(arm)

        # add individual builders
        template_sim = TemplatedSimulations(base_task=TestTask())
        template_sim.builder = self.arm_builder
        template_sim.builder = self.csv_builder
        template_sim.builder = self.yaml_builder

        # test if we have correct number of builders
        self.assertEqual(len(template_sim.builders), 1)

        # test only the last builder has been added
        self.assertTrue(isinstance(list(template_sim.builders)[0], YamlSimulationBuilder))

    def test_bad_experiment_builder(self):
        builder = SimulationBuilder()
        with self.assertRaises(ValueError) as context:
            # test 'sim' (should be 'simulation') is bad parameter for add_sweep_definition()
            builder.add_sweep_definition(lambda sim, value: {"p": value}, range(0, 2))
        self.assertTrue('passed to SweepBuilder.add_sweep_definition needs to take a simulation argument!' in str(
            context.exception.args[0]))

    def test_bad_experiment_builder1(self):
        builder = SimulationBuilder()
        with self.assertRaises(ValueError) as context:
            # test 'sim' is bad extra parameter for add_sweep_definition()
            builder.add_sweep_definition(lambda simulation, sim, value: {"p": value}, range(0, 2))
        self.assertTrue(
            'passed to SweepBuilder.add_sweep_definition needs to only have simulation and exactly one free parameter.' in str(
                context.exception.args[0]))
