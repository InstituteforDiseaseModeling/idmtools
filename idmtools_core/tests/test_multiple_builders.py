import os
from dataclasses import fields
import numpy as np
from functools import partial
from idmtools.builders import ArmSimulationBuilder, SweepArm, ArmType
from idmtools.builders import YamlSimulationBuilder
from idmtools.builders import CsvExperimentBuilder
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.test_task import TestTask


def param_update(simulation, param, value):
    return simulation.task.set_parameter(param, value)


setA = partial(param_update, param="a")
setB = partial(param_update, param="b")
setC = partial(param_update, param="c")
setD = partial(param_update, param="d")


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
