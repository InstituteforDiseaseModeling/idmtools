import os
import allure
import unittest
import pytest
from click.testing import CliRunner
os.environ['IDMTOOLS_LOGGING_USE_COLORED_LOGS'] = 'F'
os.environ['IDMTOOLS_HIDE_DEV_WARNING'] = '1'
from idmtools_cli.cli.config_file import config


@pytest.mark.smoke
@allure.story("CLI")
@allure.story("Configuration")
@allure.suite("idmtools_cli")
class TestConfigFile(unittest.TestCase):

    def test_slugify(self):
        from idmtools_cli.cli.config_file import slugify
        self.assertEqual(slugify("abc"), "ABC")
        self.assertEqual(slugify("abc def"), "ABC_DEF")

    def test_create_command(self):
        runner = CliRunner()
        result = runner.invoke(config, ['--config_path', 'blah', 'create', '--block_name', 'MY_block', '--platform','COMPS'])
        print(result.output)
