import json
from dataclasses import dataclass, field
from unittest import TestCase

import pytest

from idmtools.entities import CommandLine
from idmtools_models.json_configured_task import JSONConfiguredTask


@dataclass
class ExampleExtendedJSONConfiguredTask(JSONConfiguredTask):
    command: CommandLine = field(default=CommandLine("python -m json.tool --infile my_config.json"))
    config_file_name: str = field(default='my_config.json')


@pytest.mark.tasks
class TestJSONConfiguredTask(TestCase):

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
