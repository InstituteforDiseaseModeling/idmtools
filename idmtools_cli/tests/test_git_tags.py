import os
from functools import partial

import allure
import pytest
from idmtools_test.utils.test_task import TestTask

from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence


model_path = os.path.abspath(os.path.join("..", "..", "examples", "python_model", "inputs", "simple_python", "model.py"))


@pytest.mark.skip("skip this test since git test does not work inside container which we are using in Jenkins test")
@pytest.mark.serial
@allure.story("Entities")
@allure.story("Plugins")
@allure.suite("idmtools_core")
class TestGitTags(ITestWithPersistence):

    def setUp(self):
        self.platform = Platform("TestExecute", missing_ok=True, default_missing=dict(type='TestExecute'))

    @classmethod
    def setUpClass(cls) -> None:
        os.environ['IDMTOOLS_GIT_TAG_ADD_TO_EXPERIMENTS'] = 'y'

    @classmethod
    def tearDownClass(cls) -> None:
        os.environ['IDMTOOLS_GIT_TAG_ADD_TO_EXPERIMENTS'] = 'n'

    def test_adding_git_tag(self):
        task = TestTask()
        platform = Platform('TestExecute', missing_ok=True)
        builder = SimulationBuilder()
        def param_update(simulation, param, value):
            return simulation.task.set_parameter(param, value)

        builder.add_sweep_definition(partial(param_update, param="Run_Number"), [i for i in range(5)])
        exp = Experiment.from_builder(builder, base_task=task)
        exp.run(platform=platform, wait_until_done=True, add_git_tags_to_simulation=True)

        self.assertFalse(exp.succeeded)
        self.assertIn('git_hash', exp.tags)
        self.assertNotIn('git_hash', exp.simulations[0].tags)

    def test_adding_git_tag_as_option_to_run(self):
        task = TestTask()
        builder = SimulationBuilder()
        def param_update(simulation, param, value):
            return simulation.task.set_parameter(param, value)
        builder.add_sweep_definition(partial(param_update, param="Run_Number"), [i for i in range(5)])
        exp = Experiment.from_builder(builder, base_task=task)
        exp.run(wait_until_done=True, add_git_tags_to_simulations=True)

        self.assertFalse(exp.succeeded)
        self.assertIn('git_hash', exp.tags)
        self.assertIn('git_hash', exp.simulations[0].tags)
