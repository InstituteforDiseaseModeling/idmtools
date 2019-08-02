import unittest
import getpass
from idmtools_test.utils.cli import get_subcommands_from_help_result, run_command


class TestSystemInfoBasics(unittest.TestCase):
    @staticmethod
    def run_command(*args, start_command=None, base_command=None):
        if start_command is None:
            start_command = []
        if base_command:
            start_command.append(base_command)
        return run_command(*args, start_command=start_command)

    def test_help(self):
        """
        This test is to ensure:
        a) info --help is a valid command within the cli
        b) Help provides our expected output and options
        """
        result = self.run_command('info', '--help')
        self.assertEqual(0, result.exit_code)
        # Check for our help string
        self.assertIn('Troubleshooting and debugging information', result.output)
        # Ensure we have our expected global sub-commands
        commands = get_subcommands_from_help_result(result)
        self.assertIn('plugins', commands)
        self.assertIn('system-information', commands)

    def test_plugins_help(self):
        """
        This test is to ensure:
        a) info plugins --help is a valid command within the cli
        b) Help provides our expected output and options
        """
        result = self.run_command('info', 'plugins', '--help')
        self.assertEqual(0, result.exit_code)
        # Check for our help string
        self.assertIn('Commands to get information about installed IDM-Tools plugins', result.output)
        # Ensure we have our expected global sub-commands
        commands = get_subcommands_from_help_result(result)
        self.assertIn('cli', commands)
        self.assertIn('platform', commands)

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
                result = self.run_command('info', 'plugins', command, '--help')
                self.assertEqual(0, result.exit_code)
                # Check for our help string
                self.assertIn(help_str, result.output)

    def test_plugins_cli(self):
        """
        This test is to ensure:
        a) info plugins cli is a valid command within the cli
        b) Help provides our expected output and options
        """
        result = self.run_command('info', 'plugins', 'cli')
        # Check we got a success
        self.assertEqual(0, result.exit_code)
        # check for our table header
        self.assertIn('CLI Plugins', result.output)
        # TODO: Improve test by adding a mock CLI plugin and testing for its presence here

    def test_plugins_platform(self):
        """
        This test is to ensure:
        a) info plugins platform is a valid command within the cli
        b) Help provides our expected output and options
        """
        result = self.run_command('info', 'plugins', 'platform')
        # Check we got a success
        self.assertEqual(0, result.exit_code)
        # check for our table header
        self.assertIn('Platform Plugins', result.output)
        # TODO: Improve test by adding a mock CLI plugin and testing for its presence here

    def test_system_information_help(self):
        """
        This test is to ensure:
        a) info system_information --help is a valid command within the cli
        b) Help provides our expected output and options
        """
        result = self.run_command('info', 'system-information', '--help')
        self.assertEqual(0, result.exit_code)
        # Check for our help string
        self.assertIn('Provide an output with details about your current execution platform', result.output)

    def test_system_information_cli(self):
        """
        This test is to ensure:
        a) info system_information is a valid command within the cli
        b) Help provides our expected output and options
        """
        result = self.run_command('info', 'system-information')
        self.assertEqual(0, result.exit_code)

        self.assertIn(f'user: {getpass.getuser()}', result.output)
