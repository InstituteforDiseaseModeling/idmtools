import os
import sys
import unittest
from unittest.mock import patch
import pytest
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
import idmtools_platform_container.cli.container as container_cli
from idmtools_platform_container.utils.general import normalize_path
from .test_base import TestContainerPlatformCliBase
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


@pytest.mark.serial
class TestContainerPlatformHistoryCli(TestContainerPlatformCliBase):
    @patch('rich.console.Console.print')
    def test_history(self, mock_console):
        # first clear the history
        result = self.runner.invoke(container_cli.container, ['clear-history'])
        self.assertEqual(result.exit_code, 0)
        command = "sleep 100"
        task = CommandTask(command=command)
        experiment = Experiment.from_task(task, name="run_command")
        experiment.run(wait_until_done=False)
        # test history
        result = self.runner.invoke(container_cli.container, ['history'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual('There are 1 jobs in history.', mock_console.call_args_list[0].args[0])
        self.assertIn(normalize_path(f"{self.platform.job_directory}"),
                      mock_console.call_args_list[2].args[0])
        self.assertIn('EXPERIMENT_NAME', mock_console.call_args_list[3][0][0])
        self.assertIn('run_command', mock_console.call_args_list[3][0][0])
        self.assertIn('EXPERIMENT_ID', mock_console.call_args_list[4][0][0])
        self.assertIn(experiment.id, mock_console.call_args_list[4][0][0])
        self.assertIn('CONTAINER', mock_console.call_args_list[5][0][0])
        self.assertIn(self.platform.container_id, mock_console.call_args_list[5][0][0])
        self.assertIn('CREATED', mock_console.call_args_list[6][0][0])

        # clean up by stop the job
        result = self.runner.invoke(container_cli.container, ['cancel', experiment.id])
        self.assertEqual(result.exit_code, 0)

    def test_history_help(self):
        result = self.runner.invoke(container_cli.container, ['history', "--help"])
        expected_help = ('Usage: container history [OPTIONS] [CONTAINER_ID]\n'
                        '\n'
                        '  View the job history.\n'
                        '\n'
                        '  Arguments:\n'
                        '\n'
                        '    CONTAINER_ID: Container ID\n'
                        '\n'
                        'Options:\n'
                        '  -l, --limit INTEGER  Max number of jobs to show\n'
                        '  -n, --next INTEGER   Next number of jobs to show\n'
                        '  --help               Show this message and exit.\n')
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, expected_help)


if __name__ == '__main__':
    unittest.main()
