import os
import sys
import unittest
import re
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
        command = "python3 Assets/sleep.py 100"
        task = CommandTask(command=command)
        task.common_assets.add_asset("../inputs/sleep.py")
        experiment = Experiment.from_task(task, name="run_command")
        experiment.run(wait_until_done=False)
        job = JobHistory.get_job(experiment.id)

        # second experiment
        experiment2 = Experiment.from_task(task, name="run_command")
        experiment2.run(wait_until_done=False)
        job2 = JobHistory.get_job(experiment2.id)

        # test jobs
        result = self.runner.invoke(container_cli.container, ['jobs'])
        self.assertEqual(result.exit_code, 0)
        actual_table = get_actual_rich_table_values(mock_console)
        expected_job = ['EXPERIMENT', experiment.id, job['CONTAINER']]
        expected_job2 = ['EXPERIMENT', experiment2.id, job2['CONTAINER']]
        elapsed_ok = False
        job_ok = False
        expected_head = ['Entity Type', 'Entity ID', 'Job ID', 'Container', 'Status', 'Elapsed']
        self.assertEqual(actual_table[0], expected_head)
        for row in actual_table[1:]:
            if row[1] == experiment.id:  # if experiment id is found
                # make sure all items in expected_job are in row
                self.assertTrue(all(item in row for item in expected_job))
            if row[1] == experiment2.id:  # if experiment2 id is found
                self.assertTrue(all(item in row for item in expected_job2))

            # verify last item (Elapsed) in row is in format of 'HH:MM'
            match = re.match(r'^\d{2}:\d{2}$', row[-1])
            elapsed_ok = True if match else False

            # verify job is found
            match_job = re.match(r'^\d+$', row[2])
            job_ok = True if match_job else False
        self.assertEqual(job_ok, True)
        self.assertEqual(elapsed_ok, True)
        # # clean up container
        # result = self.runner.invoke(container_cli.container, ['stop-container', self.platform.container_id], '--remove')
        # self.assertEqual(result.exit_code, 0)

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
        for row in actual_table[1:]:
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
