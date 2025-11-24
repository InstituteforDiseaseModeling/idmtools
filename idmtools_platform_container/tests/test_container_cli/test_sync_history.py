import os
import shutil
import sys
import unittest
from unittest.mock import patch
import pytest

from idmtools.core import ItemType
from idmtools.entities import Suite
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
import idmtools_platform_container.cli.container as container_cli
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from test_base import TestContainerPlatformCliBase

@pytest.mark.serial
@pytest.mark.cli
class TestContainerPlatformSyncHistoryCli(TestContainerPlatformCliBase):
    @patch('rich.console.Console.print')
    def test_sync_history(self, mock_console):
        # first clear the history
        result = self.runner.invoke(container_cli.container, ['clear-history'])
        self.assertEqual(result.exit_code, 0)
        command = "sleep 100"
        task = CommandTask(command=command)
        experiment = Experiment.from_task(task, name="run_command")
        experiment.run(wait_until_done=False)
        # verify there is 1 job in history
        result = self.runner.invoke(container_cli.container, ['history'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual('There are 1 Experiment cache in history.', mock_console.call_args_list[0].args[0])
        # remove experiment folder
        exp_folder = self.platform.get_directory_by_id(experiment.id, ItemType.EXPERIMENT)
        shutil.rmtree(exp_folder, ignore_errors=False)
        result = self.runner.invoke(container_cli.container, ['history'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual('There are 1 Experiment cache in history.', mock_console.call_args_list[0].args[0])
        # call sync-history
        result = self.runner.invoke(container_cli.container, ['sync-history'])
        self.assertEqual(result.exit_code, 0)
        with patch('rich.console.Console.print') as mock_console1:
            result = self.runner.invoke(container_cli.container, ['history'])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual('There are 0 Experiment cache in history.', mock_console1.call_args_list[0].args[0])

        # clean up container
        result = self.runner.invoke(container_cli.container, ['stop-container', self.platform.container_id], '--remove')
        self.assertEqual(result.exit_code, 0)

    @patch('rich.console.Console.print')
    def test_sync_history_with_suite(self, mock_console):
        # first clear the history
        result = self.runner.invoke(container_cli.container, ['clear-history'])
        self.assertEqual(result.exit_code, 0)
        command = "sleep 100"
        task = CommandTask(command=command)
        experiment = Experiment.from_task(task, name="run_command")
        experiment2 = Experiment.from_task(task, name="run_command")
        suite = Suite(name="suite_name")
        suite.add_experiment(experiment)
        suite.add_experiment(experiment2)
        suite.run(wait_until_done=False)
        # verify there is 1 job in history
        result = self.runner.invoke(container_cli.container, ['history'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual('There are 2 Experiment cache in history.', mock_console.call_args_list[0].args[0])
        # remove experiment folder
        exp_folder = self.platform.get_directory_by_id(experiment.id, ItemType.EXPERIMENT)
        shutil.rmtree(exp_folder, ignore_errors=False)
        result = self.runner.invoke(container_cli.container, ['history'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual('There are 2 Experiment cache in history.', mock_console.call_args_list[0].args[0])
        # call sync-history
        result = self.runner.invoke(container_cli.container, ['sync-history'])
        self.assertEqual(result.exit_code, 0)
        with patch('rich.console.Console.print') as mock_console1:
            result = self.runner.invoke(container_cli.container, ['history'])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual('There are 1 Experiment cache in history.', mock_console1.call_args_list[0].args[0])

        # clean up container
        result = self.runner.invoke(container_cli.container, ['stop-container', self.platform.container_id], '--remove')
        self.assertEqual(result.exit_code, 0)

    def test_sync_history_help(self):
        result = self.runner.invoke(container_cli.container, ['sync-history', "--help"])
        expected_help = ('Usage: container sync-history [OPTIONS]\n'
                         '\n'
                         '  Sync the file system with job history.\n'
                         '\n'
                         'Options:\n'
                         '  --help  Show this message and exit.\n')
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, expected_help)


if __name__ == '__main__':
    unittest.main()