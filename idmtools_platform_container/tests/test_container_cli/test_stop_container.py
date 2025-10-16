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
class TestContainerPlatformStopContainerCli(TestContainerPlatformCliBase):

    @patch('rich.console.Console.print')
    def test_stop_container(self, mock_console):
        command = "sleep 100"
        task = CommandTask(command=command)
        experiment = Experiment.from_task(task, name="run_command")
        experiment.run(wait_until_done=False)
        sleep(1)
        result = self.runner.invoke(container_cli.container, ['stop-container', self.platform.container_id], '--remove')
        sleep(1)
        self.assertTrue(f"Container {self.platform.container_id} is stopped.", mock_console.call_args_list[0].args[0])

    def test_stop_container_with_stopped_container(self):
        command = "sleep 100"
        task = CommandTask(command=command)
        experiment = Experiment.from_task(task, name="run_command")
        platform = ContainerPlatform(job_directory=self.job_directory, new_container=True)
        experiment.run(wait_until_done=False, platform=platform)
        sleep(1)
        result = self.runner.invoke(container_cli.container, ['stop-container', platform.container_id])
        sleep(1)
        with patch('idmtools_platform_container.cli.container.user_logger') as mock_user_logger:
            # call stop container again to see what happens
            result = self.runner.invoke(container_cli.container, ['stop-container', platform.container_id])
            self.assertEqual(result.exit_code, 0)
            mock_user_logger.warning.assert_called_with(f"Not found running Container {platform.container_id}.")

    @patch('idmtools_platform_container.cli.container.user_logger')
    def test_stop_container_invalid(self, mock_user_logger):
        command = "sleep 100"
        platform = ContainerPlatform(job_directory=self.job_directory, new_container=True)
        task = CommandTask(command=command)
        experiment = Experiment.from_task(task, name="run_command")
        experiment.run(wait_until_done=False, platform=platform)
        sleep(1)
        result = self.runner.invoke(container_cli.container, ['stop-container', "abcd"])
        sleep(1)
        mock_user_logger.warning.assert_called_with("Not found running Container abcd.")

    def test_stop_container_help(self):
        result = self.runner.invoke(container_cli.container, ['stop-container', "--help"])
        expected_help = ('Usage: container stop-container [OPTIONS] [CONTAINER_ID]\n'
                         '\n'
                         '  Stop running container(s).\n'
                         '\n'
                         '  Arguments:\n'
                         '\n'
                         '    CONTAINER_ID: Container ID (optional)\n'
                         '\n'
                         'Options:\n'
                         '  --remove / --no-remove  Remove the container or not\n'
                         '  --help                  Show this message and exit.\n')
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, expected_help)
