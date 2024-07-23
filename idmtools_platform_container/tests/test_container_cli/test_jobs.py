import os
import sys
import unittest
from unittest.mock import patch
import pytest
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
import idmtools_platform_container.cli.container as container_cli
from idmtools_platform_container.utils.job_history import JobHistory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from helper import get_actual_rich_table_values
from test_base import TestContainerPlatformCliBase


@pytest.mark.serial
class TestContainerPlatformJobCli(TestContainerPlatformCliBase):

    @patch('rich.console.Console.print')
    def test_jobs(self, mock_console):
        command = "sleep 100"
        task = CommandTask(command=command)
        experiment = Experiment.from_task(task, name="run_command")
        experiment.run(wait_until_done=False)
        job = JobHistory.get_job(experiment.id)
        # test jobs
        result = self.runner.invoke(container_cli.container, ['jobs'])
        self.assertEqual(result.exit_code, 0)
        actual_table = get_actual_rich_table_values(mock_console)
        expected_job = ['EXPERIMENT', experiment.id, job['CONTAINER']]
        found = False
        for row in actual_table:
            if all(item in row for item in expected_job):  # if all items in expected_job are in row
                found = True  # set found to True
        self.assertEqual(found, True)
        # clean up by stop the job
        result = self.runner.invoke(container_cli.container, ['cancel', experiment.id])
        self.assertEqual(result.exit_code, 0)

    @patch('rich.console.Console.print')
    def test_jobs_with_container_id(self, mock_console):
        command = "sleep 100"
        task = CommandTask(command=command)
        experiment = Experiment.from_task(task, name="run_command")
        experiment.run(wait_until_done=False)
        job = JobHistory.get_job(experiment.id)
        # test jobs with container id
        result = self.runner.invoke(container_cli.container, ['jobs'], self.platform.container_id)
        self.assertEqual(result.exit_code, 0)
        actual_table = get_actual_rich_table_values(mock_console)
        expected_job = ['EXPERIMENT', experiment.id, job['CONTAINER']]
        found = False
        for row in actual_table:
            if all(item in row for item in expected_job):  # if all items in expected_job are in row
                found = True  # set found to True
        self.assertEqual(found, True)
        # clean up by stop the job
        result = self.runner.invoke(container_cli.container, ['cancel', experiment.id])
        self.assertEqual(result.exit_code, 0)

    def test_jobs_help(self):
        result = self.runner.invoke(container_cli.container, ['jobs', "--help"])
        expected_help = (
            'Usage: container jobs [OPTIONS] [CONTAINER_ID]\n'
            '\n'
            '  List running Experiment/Simulation jobs.\n'
            '\n'
            '  Arguments:\n'
            '\n'
            '    CONTAINER_ID: Container ID (optional)\n'
            '\n'
            'Options:\n'
            '  -l, --limit INTEGER  Max number of simulations to show\n'
            '  -n, --next INTEGER   Next number of jobs to show\n'
            '  --help               Show this message and exit.\n'
        )
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, expected_help)

if __name__ == '__main__':
    unittest.main()
