import getpass
import allure
import unittest
import pytest
from idmtools.utils.info import get_packages_from_pip
from idmtools_test.utils.cli import get_subcommands_from_help_result, run_command


@pytest.mark.smoke
@allure.story("CLI")
@allure.story("Info Command")
@allure.suite("idmtools_cli")
class TestSystemInfoBasics(unittest.TestCase):

    @pytest.mark.smoke
    def test_help(self):
        """
        This test is to ensure:
        a) info --help is a valid command within the cli
        b) Help provides our expected output and options
        """
        result = run_command('info', '--help')
        self.assertEqual(0, result.exit_code)
        # Check for our help string
        self.assertIn('Troubleshooting and debugging information', result.output)
        # Ensure we have our expected global sub-commands
        commands = get_subcommands_from_help_result(result)
        self.assertIn('plugins', commands)
        self.assertIn('system', commands)

    def test_plugins_help(self):
        """
        This test is to ensure:
        a) info plugins --help is a valid command within the cli
        b) Help provides our expected output and options
        """
        result = run_command('info', 'plugins', '--help')
        self.assertEqual(0, result.exit_code)
        # Check for our help string
        self.assertIn('Commands to get information about installed IDM-Tools plugins', result.output)
        # Ensure we have our expected global sub-commands
        commands = get_subcommands_from_help_result(result)
        self.assertIn('cli', commands)
        self.assertIn('platform', commands)
        self.assertIn('task', commands)

    def test_plugins_subcommands_help(self):
        """
        This test is to ensure:
        a) info plugins cli --help
        and  info plugins platforms --help
         is a valid command within the cli
        b) Help provides our expected output and options
        """
        subcommands = [
            ('cli', 'List CLI plugins'),
            ('platform', 'List Platform plugins')
        ]
        for command, help_str in subcommands:
            with self.subTest(f"test_plugins_{command}_help"):
                result = run_command('info', 'plugins', command, '--help')
                self.assertEqual(0, result.exit_code)
                # Check for our help string
                self.assertIn(help_str, result.output)

    @pytest.mark.skip("failed in github")
    def test_plugins_cli(self):
        """
        This test is to ensure:
        a) info plugins cli is a valid command within the cli
        b) Help provides our expected output and options
        """
        result = run_command('info', 'plugins', 'cli')
        # Check we got a success
        self.assertEqual(0, result.exit_code)
        # check for our table header
        self.assertIn('CLI Plugins', result.output)
        # TODO: Improve test by adding a mock CLI plugin and testing for its presence here

    @pytest.mark.skip("failed in github")
    def test_plugins_platform(self):
        """
        This test is to ensure:
        a) info plugins platform is a valid command within the cli
        b) Help provides our expected output and options
        """
        result = run_command('info', 'plugins', 'platform')
        # Check we got a success
        self.assertEqual(0, result.exit_code)
        # check for our table header
        self.assertIn('Platform Plugins', result.output)
        packages = get_packages_from_pip()
        if any(['idmtools-platform-comps' in p for p in packages]):
            for task in ['COMPS', 'SSMT']:
                self.assertIn(task, result.output)
        if any(['idmtools-platform-local' in p for p in packages]):
            self.assertIn('Local', result.output)

    @pytest.mark.skip("failed in github")
    def test_tasks_plugin(self):
        """
        This test is to ensure:
        a) info plugins platform is a valid command within the cli
        b) Help provides our expected output and options
        """
        result = run_command('info', 'plugins', 'task')
        # Check we got a success
        self.assertEqual(0, result.exit_code)
        packages = get_packages_from_pip()

        # check for our table header
        self.assertIn('Task Plugins', result.output)

        if any(['idmtools-models' in p for p in packages]):
            for task in ['Python', 'R', 'JSONConfigured', 'JSONConfiguredPython', 'R', 'Docker']:
                self.assertIn(task, result.output)

    def test_system_help(self):
        """
        This test is to ensure:
        a) info system --help is a valid command within the cli
        b) Help provides our expected output and options
        """
        result = run_command('info', 'system', '--help')
        self.assertEqual(0, result.exit_code)
        # Check for our help string
        self.assertIn('Provide an output with details about your current execution platform', result.output)

    @pytest.mark.skip("failed in github")
    def test_system_cli(self):
        """
        This test is to ensure:
        a) info system is a valid command within the cli
        b) Help provides our expected output and options
        """
        result = run_command('info', 'system')
        self.assertEqual(0, result.exit_code)

        self.assertIn(f'user: {getpass.getuser()}', result.output)
