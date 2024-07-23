import os
import sys
from time import sleep
from unittest.mock import patch
import pytest
import idmtools_platform_container.cli.container as container_cli
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
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
                         '  --remove / --no-remove  Display with working directory or not\n'
                         '  --help                  Show this message and exit.\n')
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, expected_help)