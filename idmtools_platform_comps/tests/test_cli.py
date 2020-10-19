import json
import os
import unittest
from logging import DEBUG
import allure
import pytest
from idmtools.core.logging import setup_logging
from idmtools_test.utils.cli import run_command, get_subcommands_from_help_result


@pytest.mark.comps
@allure.story("CLI")
class TestCompsCLI(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        # Setup logging for cli
        os.environ['IDMTOOLS_LOGGING_USER_PRINT'] = '1'
        os.environ['IDMTOOLS_HIDE_DEV_WARNING'] = '1'
        setup_logging(level=DEBUG, force=True)

    @classmethod
    def tearDownClass(cls) -> None:
        # Reset Logging
        del os.environ['IDMTOOLS_LOGGING_USER_PRINT']
        del os.environ['IDMTOOLS_HIDE_DEV_WARNING']
        setup_logging(level=DEBUG, log_filename='idmtools.log', force=True)

    @allure.feature("AssetizeOutputs")
    def test_assetize_subcommand_exists(self):
        result = run_command('comps', '--help')
        lines = get_subcommands_from_help_result(result)
        # ensure our command is in the options
        self.assertIn('assetize-outputs', lines)
        self.assertIn('login', lines)

    def test_assetize_dry_run_json(self):
        result = run_command('comps', 'Bayesian', 'assetize-outputs', '--experiment', '9311af40-1337-ea11-a2be-f0921c167861', '--dry-run', '--json', mix_stderr=False)
        self.assertTrue(result.exit_code == 0)
        files = json.loads(result.stdout)
        self.assertEqual(36, len(files))

    def test_cli_error(self):
        result = run_command('comps', 'Bayesian', 'assetize-outputs', '--experiment', '9311af40-1337-ea11-a2be-f0921c167861', '--pattern', '34234234')
        self.assertTrue(result.exit_code == -1)
        self.assertIn("No files found for related items", result.stdout)
