import os
import sys
import unittest
from time import sleep
from unittest.mock import patch
import pytest
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
import idmtools_platform_container.cli.container as container_cli

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)
from test_base import TestContainerPlatformCliBase


@pytest.mark.serial
@pytest.mark.cli
class TestContainerPlatformIsRunningCli(TestContainerPlatformCliBase):

    def test_is_running(self):
        command = "python3 Assets/sleep.py"
        task = CommandTask(command=command)
        task.common_assets.add_asset(os.path.join(script_dir, "..", "inputs", "sleep.py"))
        experiment = Experiment.from_task(task, name="run_command")
        experiment.run(wait_until_done=False)
        sleep(10)
        # test is-running with experiment id
        with patch('rich.console.Console.print') as mock_console_exp:
            result = self.runner.invoke(container_cli.container, ['is-running', experiment.id])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(f'EXPERIMENT {experiment.id} is running on container {self.platform.container_id}.',
                             mock_console_exp.call_args_list[0][0][0])
        # test is-running with simulation id
        with patch('rich.console.Console.print') as mock_console_sim:
            result = self.runner.invoke(container_cli.container, ['is-running', experiment.simulations[0].id])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                f'SIMULATION {experiment.simulations[0].id} is running on container {self.platform.container_id}.',
                mock_console_sim.call_args_list[0][0][0])
        # test is-running with invalid id
        with patch('rich.console.Console.print') as mock_console_invalid:
            result = self.runner.invoke(container_cli.container, ['is-running', "abc"])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(f'Job abc is not found.', mock_console_invalid.call_args_list[0][0][0])

        # test is-running with suite id
        with patch('rich.console.Console.print') as mock_console_suite:
            result = self.runner.invoke(container_cli.container, ['is-running', experiment.parent_id])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(f'{experiment.parent_id} is not a valid Experiment/Simulation ID.',
                             mock_console_suite.call_args_list[0][0][0])

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
