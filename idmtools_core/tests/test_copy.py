import copy
import allure
import os
from functools import partial
import pytest
from idmtools_test.utils.test_task import TestTask

from idmtools.assets import Asset
from idmtools.core.platform_factory import Platform
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence

DEFAULT_CONFIG_PATH = os.path.join(COMMON_INPUT_PATH, "files", "config.json")
DEFAULT_CAMPAIGN_JSON = os.path.join(COMMON_INPUT_PATH, "files", "campaign.json")
DEFAULT_DEMOGRAPHICS_JSON = os.path.join(COMMON_INPUT_PATH, "files", "demographics.json")
DEFAULT_ERADICATION_PATH = os.path.join(COMMON_INPUT_PATH, "emod", "Eradication.exe")


def param_update(simulation, param, value):
    return simulation.task.set_parameter(param, value)


class setParam:
    def __init__(self, param):
        self.param = param

    def __call__(self, simulation, value):
        return param_update(simulation, self.param, value)


setA = partial(param_update, param="a")


@pytest.mark.smoke
@allure.story("Core")
@allure.suite("idmtools_core")
class TestCopy(ITestWithPersistence):

    def setUp(self):
        super().setUp()
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        print(self.case_name)

    def tearDown(self):
        super().tearDown()

    def test_deepcopy_assets(self):
        test_platform = Platform("TestExecute", missing_ok=True)
        task = CommandTask(command="python --version")
        e = Experiment.from_task(task=task, name="Example of experiment from task")
        e.add_asset(os.path.join(COMMON_INPUT_PATH, 'python_experiments', "model.py"))
        e.simulations[0].assets.add_asset(Asset(absolute_path=os.path.join(COMMON_INPUT_PATH, 'files', "config.json")))

        # test deepcopy of experiment
        e.pre_creation(test_platform)
        ep = copy.deepcopy(e)
        self.assertEqual(len(ep.assets.assets), 1)
        ep.assets = copy.deepcopy(e.assets)
        self.assertEqual(len(ep.assets.assets), 1)
        self.assertEqual(e.assets, ep.assets)

        # test deepcopy of simulation
        sim: Simulation = e.simulations[0]
        sim2 = copy.deepcopy(sim)
        self.assertEqual(len(sim2.assets.assets), 0)
        sim2.assets = copy.deepcopy(sim.assets)
        self.assertEqual(len(sim.assets), 1)
        self.assertEqual(sim.assets, sim.assets)

    def test_deepcopy_experiment(self):
        test_platform = Platform("TestExecute", missing_ok=True)
        task = TestTask()
        ts = TemplatedSimulations(base_task=task)
        e = Experiment.from_template(ts)
        e.add_asset(os.path.join(COMMON_INPUT_PATH, 'python_experiments', "model.py"))
        from idmtools.builders import SimulationBuilder
        builder = SimulationBuilder()
        builder.add_sweep_definition(setA, range(10))
        builder.add_sweep_definition(setParam("b"), [1, 2, 3])
        e.simulations.add_builder(builder)

        e.gather_assets()

        self.assertEqual(len(ts.builders), 1)
        self.assertEqual(len(e.simulations), 30)
        e.pre_creation(test_platform)
        self.assertEqual(len(e.assets.assets), 1)

        # test deepcopy of experiment
        ep = copy.deepcopy(e)

        # the templates will become a true list since we cannot copy generators
        self.assertIsInstance(ep.simulations.items, list)
        self.assertEqual(len(ep.simulations), 30)
        self.assertEqual(len(ep.assets.assets), 1)
        self.assertEqual(e, ep)

        with self.assertRaises(AssertionError) as context:
            self.assertDictEqual(vars(e), vars(ep))
        self.assertIn('Set self.maxDiff to None to see it', context.exception.args[0])

    def test_deepcopy_simulation(self):
        test_platform = Platform("TestExecute", missing_ok=True)
        task = TestTask()
        sim = Simulation.from_task(task=task)

        sim.pre_creation(test_platform)
        self.assertEqual(len(sim.assets.assets), 1)

        # test deepcopy of simulation
        sp = copy.deepcopy(sim)
        self.assertEqual(len(sp.assets.assets), 0)
        # exclude the common assets
        setattr(sp.task, 'common_assets', None)
        sim.task.common_assets = None
        self.assertEqual(sim, sp)

