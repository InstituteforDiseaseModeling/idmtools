import allure
import os
from functools import partial
import pytest
from COMPS.Data import QueryCriteria
from idmtools.builders import SimulationBuilder, SweepArm, ArmType, ArmSimulationBuilder
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools_test.utils.utils import get_case_name

# define specific callbacks for a, b, and c
setA = partial(JSONConfiguredPythonTask.set_parameter_sweep_callback, param="a")
setB = partial(JSONConfiguredPythonTask.set_parameter_sweep_callback, param="b")
setC = partial(JSONConfiguredPythonTask.set_parameter_sweep_callback, param="c")
setD = partial(JSONConfiguredPythonTask.set_parameter_sweep_callback, param="d")
setE = partial(JSONConfiguredPythonTask.set_parameter_sweep_callback, param="e")

@pytest.mark.comps
@pytest.mark.serial
@allure.story("COMPS")
class TestSimulationBuilder(ITestWithPersistence):
    @classmethod
    def setUpClass(cls) -> None:
        cls.platform = Platform('SlurmStage')

    def setUp(self) -> None:
        self.case_name = get_case_name(os.path.basename(__file__) + "--" + self._testMethodName)

    def testArmSimulationBuilderWithCumulateArm(self):
        """
            This is a test to demonstrate how to use 1 arm in ArmSimulationBuilder to continuously add to arm after call
            to builder.add_arm(arm).
            |__sweep arm
                |_ a = 1
                |_ b = [2,3]
                |_ c = [4,5]
            sweep the same arm by continuously to add more parameters after called: builder.add_arm(arm)
                |_ d = [6,7]
                |_ e = 2
            Expect sims with parameters:
                sim1: {a:1, b:2, c:4}
                sim2: {a:1, b:2, c:5}
                sim3: {a:1, b:3, c:4}
                sim4: {a:1, b:3, c:5}
                sim5: {a:1, b:2, c:4, d:6, e:2}
                sim6: {a:1, b:2, c:4, d:7, e:2}
                sim7: {a:1, b:2, c:5, d:6, e:2}
                sim8: {a:1, b:2, c:5, d:7, e:2}
                sim9: {a:1, b:3, c:4, d:6, e:2}
                sim10: {a:1, b:3, c:4, d:7, e:2}
                sim11: {a:1, b:3, c:5, d:6, e:2}
                sim12: {a:1, b:3, c:5, d:7, e:2}
        """
        base_task = JSONConfiguredPythonTask(script_path=os.path.join(COMMON_INPUT_PATH, "python", "model1.py"))
        # define that we are going to create multiple simulations from this task
        ts = TemplatedSimulations(base_task=base_task)

        # define our first SweepArm
        arm = SweepArm(type=ArmType.cross)
        builder = ArmSimulationBuilder()
        arm.add_sweep_definition(setA, 1)
        arm.add_sweep_definition(setB, [2, 3])
        arm.add_sweep_definition(setC, [4, 5])
        builder.add_arm(arm)
        # adding more simulations with sweeping
        arm.add_sweep_definition(setD, [6, 7])
        arm.add_sweep_definition(setE, [2])
        builder.add_arm(arm)

        # add our builders to our template
        ts.add_builder(builder)

        # create experiment from the template
        experiment = Experiment.from_template(ts, name=self.case_name)
        experiment.run(wait_until_done=True)
        self.assertTrue(experiment.succeeded)
        comps_exp = self.platform.get_item(experiment.id, item_type=ItemType.EXPERIMENT, raw=True)
        comps_simulations = comps_exp.get_simulations(query_criteria=QueryCriteria().select_children("tags"))
        self.assertEqual(comps_simulations.__len__(), 12)
        exclude_key = "task_type"
        real_tags = [
            {key: int(value) for key, value in simulation.tags.items() if key != exclude_key}
            for simulation in comps_simulations
        ]
        expected_tags = [
            {'a': 1, 'b': 2, 'c': 4},
            {'a': 1, 'b': 2, 'c': 5},
            {'a': 1, 'b': 3, 'c': 4},
            {'a': 1, 'b': 3, 'c': 5},
            {'a': 1, 'b': 2, 'c': 4, 'd': 6, 'e': 2},
            {'a': 1, 'b': 2, 'c': 4, 'd': 7, 'e': 2},
            {'a': 1, 'b': 2, 'c': 5, 'd': 6, 'e': 2},
            {'a': 1, 'b': 2, 'c': 5, 'd': 7, 'e': 2},
            {'a': 1, 'b': 3, 'c': 4, 'd': 6, 'e': 2},
            {'a': 1, 'b': 3, 'c': 4, 'd': 7, 'e': 2},
            {'a': 1, 'b': 3, 'c': 5, 'd': 6, 'e': 2},
            {'a': 1, 'b': 3, 'c': 5, 'd': 7, 'e': 2}
        ]
        sorted_real_tags = sorted(real_tags, key=lambda x: sorted(x.items()))
        sorted_expected_tags = sorted(expected_tags, key=lambda x: sorted(x.items()))
        self.assertEqual(sorted_real_tags, sorted_expected_tags)

    def testArmSimulationBuilderWithTwoArms(self):
        """
            This is a test to demonstrate how to use 2 arms in ArmSimulationBuilder.

            |__sweep arm1
                |_ a = 1
                |_ b = [2,3]
                |_ c = [4,5]
            |__ sweep arm2
                |_ d = [6,7]
                |_ e = 2
            Expect sims with parameters:
                sim1: {a:1, b:2, c:4}
                sim2: {a:1, b:2, c:5}
                sim3: {a:1, b:3, c:4}
                sim4: {a:1, b:3, c:5}
                sim5: {d:6, e:2}
                sim6: {d:7, e:2}
            Note:
                arm1 and arm2 are adding to total simulations
        """
        base_task = JSONConfiguredPythonTask(script_path=os.path.join(COMMON_INPUT_PATH, "python", "model1.py"))
        # define that we are going to create multiple simulations from this task
        ts = TemplatedSimulations(base_task=base_task)

        # define our first SweepArm
        arm = SweepArm(type=ArmType.cross)
        builder = ArmSimulationBuilder()
        arm.add_sweep_definition(setA, 1)
        arm.add_sweep_definition(setB, [2, 3])
        arm.add_sweep_definition(setC, [4, 5])
        builder.add_arm(arm)

        # define our second SweepArm
        arm2 = SweepArm(type=ArmType.cross)
        arm2.add_sweep_definition(setD, [6, 7])
        arm2.add_sweep_definition(setE, [2])
        builder.add_arm(arm2)

        # add our builders to our template
        ts.add_builder(builder)

        # create experiment from the template
        experiment = Experiment.from_template(ts, name=self.case_name)
        experiment.run(wait_until_done=True)
        self.assertTrue(experiment.succeeded)
        self.assertEqual(experiment.simulations.__len__(), 6)

    def testArmSimulationBuilderWithTwoArms1(self):
        """
        This is a test to demonstrate how to use 2 arms in ArmSimulationBuilder but achieve the same result as
        testArmSimulationBuilderWithCumulateArm
        """
        base_task = JSONConfiguredPythonTask(script_path=os.path.join(COMMON_INPUT_PATH, "python", "model1.py"))
        # define that we are going to create multiple simulations from this task
        ts = TemplatedSimulations(base_task=base_task)

        # define our first SweepArm
        arm1 = SweepArm(type=ArmType.cross)
        arm2 = SweepArm(type=ArmType.cross)

        builder = ArmSimulationBuilder()
        arm1.add_sweep_definition(setA, 1)
        arm1.add_sweep_definition(setB, [2, 3])
        arm1.add_sweep_definition(setC, [4, 5])
        builder.add_arm(arm1)
        arm2.add_sweep_definition(setA, 1)
        arm2.add_sweep_definition(setB, [2, 3])
        arm2.add_sweep_definition(setC, [4, 5])
        # adding more simulations with sweeping
        arm2.add_sweep_definition(setD, [6, 7])
        arm2.add_sweep_definition(setE, [2])
        builder.add_arm(arm2)

        ts.add_builder(builder)
        experiment = Experiment.from_template(ts, name=self.case_name)
        # run experiment
        experiment.run(wait_until_done=True)
        self.assertTrue(experiment.succeeded)
        self.assertEqual(experiment.simulations.__len__(), 12)

    def testSimulationBuilder(self):
        """
            This file demonstrates how to use SimulationBuilder.

            |__SimulationBuilder1
                |_ a = 1
                |_ b = [2,3]
                |_ c = [4,5]
             --SimulationBuilder2
                |_ d = [6,7]
                |_ e = 2
            Expect sims with parameters:
                sim1: {a:1, b:2, c:4}
                sim2: {a:1, b:2, c:5}
                sim3: {a:1, b:3, c:4}
                sim4: {a:1, b:3, c:5}
                sim5: {d:6, e:2}
                sim6: {d:7, e:2}
            Note:
                builder1 and builder2 are adding to total simulations
        """
        base_task = JSONConfiguredPythonTask(script_path=os.path.join(COMMON_INPUT_PATH, "python", "model1.py"))
        # define that we are going to create multiple simulations from this task
        ts = TemplatedSimulations(base_task=base_task)

        # define our first SimulationBuilder
        builder1 = SimulationBuilder()
        builder1.add_sweep_definition(setA, 1)
        builder1.add_sweep_definition(setB, [2, 3])
        builder1.add_sweep_definition(setC, [4, 5])
        ts.add_builder(builder1)
        builder2 = SimulationBuilder()
        builder2.add_sweep_definition(setD, [6, 7])
        builder2.add_sweep_definition(setE, [2])
        ts.add_builder(builder2)

        # create experiment from the template
        experiment = Experiment.from_template(ts, name=self.case_name)
        experiment.run(wait_until_done=True)
        self.assertTrue(experiment.succeeded)
        comps_exp = self.platform.get_item(experiment.id, item_type=ItemType.EXPERIMENT, raw=True)
        comps_simulations = comps_exp.get_simulations(query_criteria=QueryCriteria().select_children("tags"))
        self.assertEqual(comps_simulations.__len__(), 6)
        exclude_key = "task_type"
        real_tags = [
            {key: int(value) for key, value in simulation.tags.items() if key != exclude_key}
            for simulation in comps_simulations
        ]
        expected_tags = [
            {'a': 1, 'b': 2, 'c': 4},
            {'a': 1, 'b': 2, 'c': 5},
            {'a': 1, 'b': 3, 'c': 4},
            {'a': 1, 'b': 3, 'c': 5},
            {'d': 6, 'e': 2},
            {'d': 7, 'e': 2}
        ]
        sorted_real_tags = sorted(real_tags, key=lambda x: sorted(x.items()))
        sorted_expected_tags = sorted(expected_tags, key=lambda x: sorted(x.items()))
        self.assertEqual(sorted_real_tags, sorted_expected_tags)
