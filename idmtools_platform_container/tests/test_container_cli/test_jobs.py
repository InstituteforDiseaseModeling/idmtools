import os
import sys
import unittest
import pytest
from click.testing import CliRunner
from idmtools.core.platform_factory import Platform
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
import idmtools_platform_container.cli.container as container_cli
from idmtools_platform_container.utils.job_history import JobHistory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from helper import get_jobs_from_cli


@pytest.mark.serial
class TestContainerPlatformJobCli(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.job_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "DEST")
        self.platform = Platform("Container", job_directory=self.job_directory)


    def tearDown(self):
        pass

    def test_jobs(self):
        command = "sleep 100"
        task = CommandTask(command=command)
        experiment = Experiment.from_task(task, name="run_command")
        experiment.run(wait_until_done=False)
        job = JobHistory.get_job(experiment.id)
        # test jobs
        actual_table = get_jobs_from_cli(self.runner)
        expected_job = ['EXPERIMENT', experiment.id, job['CONTAINER']]
        found = False
        for row in actual_table:
            if all(item in row for item in expected_job):  # if all items in expected_job are in row
                found = True  # set found to True
        self.assertEqual(found, True)
        # clean up by stop the job
        result = self.runner.invoke(container_cli.container, ['cancel', experiment.id])
        self.assertEqual(result.exit_code, 0)

    def test_jobs_with_container_id(self):
        command = "sleep 100"
        task = CommandTask(command=command)
        experiment = Experiment.from_task(task, name="run_command")
        experiment.run(wait_until_done=False)
        job = JobHistory.get_job(experiment.id)
        # test jobs with container id
        actual_table = get_jobs_from_cli(self.runner, job['CONTAINER'])
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
