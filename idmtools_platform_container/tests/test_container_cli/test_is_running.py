import os
import sys
import unittest
from time import sleep
from unittest.mock import patch
import pytest
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
import idmtools_platform_container.cli.container as container_cli
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from test_base import TestContainerPlatformCliBase


@pytest.mark.serial
class TestContainerPlatformIsRunningCli(TestContainerPlatformCliBase):

    @patch('rich.console.Console.print')
    def test_is_running(self, mock_console):
        command = "sleep 100"
        task = CommandTask(command=command)
        experiment = Experiment.from_task(task, name="run_command")
        experiment.run(wait_until_done=False)
        sleep(10)
        result = self.runner.invoke(container_cli.container, ['is-running', experiment.id])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(f'EXPERIMENT {experiment.id} is running on container {self.platform.container_id}.',
                         mock_console.call_args_list[0][0][0])
        # clean up container
        result = self.runner.invoke(container_cli.container, ['stop-container', self.platform.container_id], '--remove')
        self.assertEqual(result.exit_code, 0)

    def test_is_running_help(self):
        result = self.runner.invoke(container_cli.container, ['is-running', "--help"])
        expected_help = (
            'Usage: container is-running [OPTIONS] ITEM_ID\n'
            '\n'
            '  Check if an Experiment/Simulation is running.\n'
            '\n'
            '  Arguments:\n'
            '\n'
            '    ITEM_ID: Experiment/Simulation ID\n'
            '\n'
            'Options:\n'
            '  --help  Show this message and exit.\n'
        )
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, expected_help)


if __name__ == '__main__':
    unittest.main()
