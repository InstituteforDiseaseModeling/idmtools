import os
import re
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
import pytest
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
import idmtools_platform_container.cli.container as container_cli
from idmtools_platform_container.container_platform import ContainerPlatform
from idmtools_platform_container.utils.general import normalize_path

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from test_base import TestContainerPlatformCliBase
from helper import cleaned_str


@pytest.mark.serial
@pytest.mark.cli
class TestContainerPlatformHistoryCli(TestContainerPlatformCliBase):
    @patch('rich.console.Console.print')
    def test_history(self, mock_console):
        # first clear the history
        result = self.runner.invoke(container_cli.container, ['clear-history'])
        self.assertEqual(result.exit_code, 0)
        command = "sleep 100"
        platform = ContainerPlatform(job_directory=self.job_directory, new_container=True)
        task = CommandTask(command=command)
        experiment = Experiment.from_task(task, name="run_command")
        experiment.run(wait_until_done=False, platform=platform)
        # test history
        result = self.runner.invoke(container_cli.container, ['history'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual('There are 1 Experiment cache in history.', mock_console.call_args_list[0].args[0])
        self.assertIn(normalize_path(f"{platform.job_directory}"),
                      mock_console.call_args_list[2].args[0])
        self.assertEqual('EXPERIMENT_NAME : run_command', cleaned_str(mock_console.call_args_list[3][0][0]))
        self.assertEqual(f'EXPERIMENT_ID   : {experiment.id}', cleaned_str(mock_console.call_args_list[4][0][0]))
        self.assertEqual(f'CONTAINER       : {platform.container_id}',
                          cleaned_str(mock_console.call_args_list[5][0][0]))
        match_created_time = re.match(r'^CREATED         : \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$',
                                      cleaned_str(mock_console.call_args_list[6][0][0]))
        self.assertTrue(match_created_time)
        # Verify history path:
        JOB_HISTORY_DIR = "idmtools_experiment_history"
        history_path = Path.home().joinpath(".idmtools").joinpath(JOB_HISTORY_DIR)
        self.assertTrue(history_path.is_dir())
        self.assertTrue(any(history_path.iterdir()))  # verify history path has some files

        # clean up container
        result = self.runner.invoke(container_cli.container, ['stop-container', platform.container_id, '--remove'])
        self.assertEqual(result.exit_code, 0)

    @patch('rich.console.Console.print')
    def test_history_with_container(self, mock_console):
        # first clear the history
        result = self.runner.invoke(container_cli.container, ['clear-history'])
        self.assertEqual(result.exit_code, 0)
        command = "sleep 100"
        task = CommandTask(command=command)
        platform = ContainerPlatform(job_directory=self.job_directory, new_container=True)
        task = CommandTask(command=command)
        experiment = Experiment.from_task(task, name="run_command")
        experiment.run(wait_until_done=False, platform=platform)
        # test history
        result = self.runner.invoke(container_cli.container, ['history', platform.container_id])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual('There are 1 Experiment cache in history.', mock_console.call_args_list[0].args[0])
        self.assertIn(normalize_path(f"{platform.job_directory}"),
                      mock_console.call_args_list[2].args[0])
        self.assertEqual('EXPERIMENT_NAME : run_command', cleaned_str(mock_console.call_args_list[3][0][0]))
        self.assertEqual(f'EXPERIMENT_ID   : {experiment.id}', cleaned_str(mock_console.call_args_list[4][0][0]))
        self.assertEqual(f'CONTAINER       : {platform.container_id}',
                          cleaned_str(mock_console.call_args_list[5][0][0]))
        match_created_time = re.match(r'^CREATED         : \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$',
                                      cleaned_str(mock_console.call_args_list[6][0][0]))
        self.assertTrue(match_created_time)

        # clean up container
        result = self.runner.invoke(container_cli.container, ['stop-container', platform.container_id, '--remove'])
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