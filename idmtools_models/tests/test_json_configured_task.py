import allure
import json
from dataclasses import dataclass, field
from unittest import TestCase
import pytest
from idmtools.core.platform_factory import Platform
from idmtools.core.task_factory import TaskFactory
from idmtools.entities import CommandLine
from idmtools.entities.experiment import Experiment
from idmtools_models.json_configured_task import JSONConfiguredTask


@dataclass
class ExampleExtendedJSONConfiguredTask(JSONConfiguredTask):
    command: CommandLine = field(default=None)
    config_file_name: str = field(default='my_config.json')

    def __post_init__(self):
        if self.command is None:
            self.command = CommandLine.from_string('python -m json.tool --infile my_config.json')

@pytest.mark.tasks
@pytest.mark.smoke
@allure.story("JSONConfiguredTask")
@allure.suite("idmtools_models")
class TestJSONConfiguredTask(TestCase):

    def setUp(self) -> None:
        TaskFactory().register_task(ExampleExtendedJSONConfiguredTask)

    @staticmethod
    def get_cat_command_task(extra_opts=None):
        example_command = 'cat config.json'
        opts = dict(command=example_command)
        if extra_opts:
            opts.update(extra_opts)
        task = JSONConfiguredTask(**opts)
        return task

    def test_config_asset_works(self):
        task = self.get_cat_command_task()
        task.set_parameter('a', 1)
        task.gather_all_assets()

        self.assertEqual(str(task.command), 'cat config.json')
        self.assertEqual(len(task.transient_assets.assets), 1)
        self.assertEqual(task.gather_transient_assets().assets[0].filename, 'config.json')
        self.assertDictEqual(json.loads(task.transient_assets.assets[0].content), {'a': 1})

        # test that we only keep one config
        task.set_parameter('a', 2)
        task.gather_all_assets()
        self.assertEqual(len(task.transient_assets.assets), 1)
        self.assertDictEqual(json.loads(task.transient_assets.assets[0].content), {'a': 2})

    def test_update_multiple(self):
        task = self.get_cat_command_task()
        values = dict(a='1', b=2, c=3.2, d=4)
        task.update_parameters(values)

        task.gather_all_assets()
        self.assertEqual(str(task.command), 'cat config.json')
        self.assertDictEqual(json.loads(task.transient_assets.assets[0].content), values)

    def test_derived_class(self):
        task = ExampleExtendedJSONConfiguredTask()
        task.set_parameter('a', 23)
        task.gather_all_assets()

        self.assertEqual(str(task.command), 'python -m json.tool --infile my_config.json')
        self.assertEqual(len(task.transient_assets.assets), 1)
        self.assertEqual(task.transient_assets.assets[0].filename, 'my_config.json')

    def test_envelope(self):
        task = self.get_cat_command_task(dict(envelope='test'))
        values = dict(a='1', b=2, c=3.2, d=4)
        task.update_parameters(values)

        task.gather_all_assets()
        self.assertEqual(str(task.command), 'cat config.json')
        self.assertDictEqual(json.loads(task.transient_assets.assets[0].content), dict(test=values))

    @pytest.mark.timeout(60)
    @pytest.mark.serial
    def test_reload_from_simulation_task(self):
        with Platform("TestExecute", missing_ok=True, default_missing=dict(type='TestExecute')) as p:
            task = ExampleExtendedJSONConfiguredTask(parameters=dict(a=1, b=2, c=3))
            experiment = Experiment.from_task(task=task, name="Test Reload Simulation")
            experiment.run(wait_until_done=True)
            experiment2 = Experiment.from_id(experiment.id, load_task=True)
            self.assertEqual(experiment.id, experiment2.id)
            self.assertEqual(1, experiment2.simulation_count)
            self.assertEqual(experiment.simulations[0].id, experiment2.simulations[0].id)
            sim = experiment2.simulations[0]
            self.assertEqual(task.parameters, sim.task.parameters)
            self.assertEqual(task.command, sim.task.command)

