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
class TestContainerPlatformInspectCli(TestContainerPlatformCliBase):

    @patch('rich.console.Console.print')
    def test_inspect(self, mock_console):
        command = "sleep 100"
        task = CommandTask(command=command)
        experiment = Experiment.from_task(task, name="run_command")
        experiment.run(wait_until_done=False)
        sleep(1)
        result = self.runner.invoke(container_cli.container, ['inspect', self.platform.container_id])
        self.assertIn('Container ID', mock_console.call_args_list[1][0][0])
        self.assertIn(f'{self.platform.container_id}', mock_console.call_args_list[1][0][0])
        self.assertIn('Container Name', mock_console.call_args_list[2][0][0])
        self.assertIn('Status', mock_console.call_args_list[3][0][0])
        self.assertIn('Created', mock_console.call_args_list[4][0][0])
        self.assertIn('StartedAt', mock_console.call_args_list[5][0][0])
        self.assertIn('Image', mock_console.call_args_list[6][0][0])
        self.assertIn(f'{self.platform.docker_image}', mock_console.call_args_list[7][0][0].text.plain)
        self.assertIn('Image Tags', mock_console.call_args_list[8][0][0])
        self.assertIn('State', mock_console.call_args_list[10][0][0])
        self.assertIn('Mounts', mock_console.call_args_list[12][0][0])

    def test_inspect_help(self):
        result = self.runner.invoke(container_cli.container, ['inspect', "--help"])
        expected_help = ('Usage: container inspect [OPTIONS] CONTAINER_ID\n'
                         '\n'
                         '  Inspect a container.\n'
                         '\n'
                         '  Arguments:\n'
                         '\n'
                         '    CONTAINER_ID: Container ID\n'
                         '\n'
                         'Options:\n'
                         '  --help  Show this message and exit.\n')
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, expected_help)