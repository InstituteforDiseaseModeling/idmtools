import json
import os
import unittest
import pytest
os.environ['IDMTOOLS_USE_PRINT_OUTPUT'] = '1'
os.environ['IDMTOOLS_HIDE_DEV_WARNING'] = '1'
from idmtools_test.utils.cli import run_command, get_subcommands_from_help_result


@pytest.mark.comps
class TestCompsCLI(unittest.TestCase):
    def test_assetize_subcommand_exists(self):
        result = run_command('comps', '--help')
        lines = get_subcommands_from_help_result(result)
        # ensure our command is in the options
        self.assertIn('assetize-outputs', lines)

    def test_assetize_dry_run_json(self):
        result = run_command('comps', 'Bayesian', 'assetize-outputs', '--experiment', '9311af40-1337-ea11-a2be-f0921c167861', '--dry-run', '--json', mix_stderr=False)
        self.assertTrue(result.exit_code == 0)
        files = json.loads(result.stdout)
        self.assertEqual(36, len(files))

    def test_cli_error(self):
        result = run_command('comps', 'Bayesian', 'assetize-outputs', '--experiment', '9311af40-1337-ea11-a2be-f0921c167861', '--pattern', '34234234')
        self.assertTrue(result.exit_code == -1)
        self.assertIn("No files found for related items", result.stdout)
