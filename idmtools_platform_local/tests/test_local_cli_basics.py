# flake8: noqa E402
from idmtools_test.utils.confg_local_runner_test import config_local_test
local_path = config_local_test()
import unittest
from idmtools_test.utils.cli import get_subcommands_from_help_result, run_command


class TestLocalCLIBasic(unittest.TestCase):
    @staticmethod
    def run_command(*args, start_command=None, base_command=None):
        if start_command is None:
            start_command = []
        if base_command:
            start_command.append(base_command)
        return run_command(*args, start_command=start_command)

    def test_load(self):
        result = self.run_command('experiment', '--platform', 'Local', '--help', base_command='')
        lines = get_subcommands_from_help_result(result)
        # ensure our command is in the options
        self.assertIn('status', lines)

    def test_status(self):
        result = self.run_command('experiment', '--platform', 'Local', 'status', base_command='')
        print(result)
