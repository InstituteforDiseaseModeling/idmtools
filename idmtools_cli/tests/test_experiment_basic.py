import allure
import unittest
import pytest
from idmtools_test.utils.cli import get_subcommands_from_help_result, run_command


@pytest.mark.smoke
@allure.story("CLI")
@allure.suite("idmtools_cli")
class TestExperimentBasics(unittest.TestCase):

    def test_help(self):
        """
        This test is to ensure:
        a) experiment --help is a valid command within the cli
        b) Help provides our expected output and options
        c) Checks for command sub-commands
        Returns:

        """
        result = run_command('experiment', '--help')
        # Check for our help string
        self.assertIn('Contains commands related to experiments', result.output)
        # Check that there is a --platform option
        self.assertIn('--platform', result.output)
        # Ensure we have our expected global sub-commands
        commands = get_subcommands_from_help_result(result)
        self.assertIn('status', commands)
