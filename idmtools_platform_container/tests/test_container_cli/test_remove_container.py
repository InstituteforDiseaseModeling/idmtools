import os
import sys
from time import sleep
from unittest.mock import patch
import pytest
import idmtools_platform_container.cli.container as container_cli
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
from idmtools_platform_container.container_platform import ContainerPlatform

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from test_base import TestContainerPlatformCliBase


@pytest.mark.serial
@pytest.mark.cli
class TestContainerPlatformRemoveContainerCli(TestContainerPlatformCliBase):

    @patch('rich.console.Console.print')
    def test_remove_container(self, mock_console):
        command = "sleep 100"
        task = CommandTask(command=command)
        experiment = Experiment.from_task(task, name="run_command")
        platform = ContainerPlatform(job_directory=self.job_directory, new_container=True)
        experiment.run(wait_until_done=False, platform=platform)
        result = self.runner.invoke(container_cli.container, ['stop-container', platform.container_id])
        self.assertEqual(result.exit_code, 0)
        sleep(1)
        result = self.runner.invoke(container_cli.container, ['remove-container', platform.container_id])
        self.assertEqual(result.exit_code, 0)
        with patch('rich.console.Console.print') as mock_console:
            result = self.runner.invoke(container_cli.container, ['inspect', platform.container_id])
            self.assertEqual(result.exit_code, 0)
            self.assertTrue(f"Container {platform.container_id} not found.", mock_console.call_args_list[0].args[0])

    @patch('idmtools_platform_container.cli.container.user_logger')
    def test_remove_container_running_container(self, mock_user_logger):
        command = "sleep 100"
        task = CommandTask(command=command)
        experiment = Experiment.from_task(task, name="run_command")
        platform = ContainerPlatform(job_directory=self.job_directory, new_container=True)
        experiment.run(wait_until_done=False, platform=platform)
        result = self.runner.invoke(container_cli.container, ['remove-container', platform.container_id])
        self.assertEqual(result.exit_code, 0)
        mock_user_logger.warning.assert_called_with(
            f"Container {platform.container_id} is running, need to stop first.")

        result = self.runner.invoke(container_cli.container, ['stop-container', platform.container_id, '--remove'])
        self.assertEqual(result.exit_code, 0)

    @patch('idmtools_platform_container.cli.container.user_logger')
    def test_remove_container_invalid(self, mock_user_logger):
        command = "sleep 100"
        platform = ContainerPlatform(job_directory=self.job_directory, new_container=True)
        task = CommandTask(command=command)
        experiment = Experiment.from_task(task, name="run_command")
        experiment.run(wait_until_done=False, platform=platform)
        sleep(1)
        result = self.runner.invoke(container_cli.container, ['remove-container', "abcd"])
        sleep(1)
        mock_user_logger.warning.assert_called_with("Container abcd not found.")
        result = self.runner.invoke(container_cli.container, ['stop-container', platform.container_id, '--remove'])
        self.assertEqual(result.exit_code, 0)

    def test_remove_container_help(self):
        result = self.runner.invoke(container_cli.container, ['remove-container', "--help"])
        expected_help = ('Usage: container remove-container [OPTIONS] [CONTAINER_ID]\n'
                         '\n'
                         '  Remove stopped containers.\n'
                         '\n'
                         '  Arguments:\n'
                         '\n'
                         '    CONTAINER_ID: Container ID (optional)\n'
                         '\n'
                         'Options:\n'
                         '  --help  Show this message and exit.\n')
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, expected_help)
