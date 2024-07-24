import os
import sys
import unittest
from unittest import mock
from unittest.mock import patch
import pytest
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
import idmtools_platform_container.cli.container as container_cli
from idmtools_platform_container.utils.general import normalize_path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from test_base import TestContainerPlatformCliBase


@pytest.mark.serial
class TestContainerPlatformStatusCli(TestContainerPlatformCliBase):
    @patch('rich.console.Console.print')
    def test_status_with_experiment_id(self, mock_console):
        command = "sleep 100"
        task = CommandTask(command=command)
        experiment = Experiment.from_task(task, name="run_command")
        experiment.run(wait_until_done=False)
        # test status with experiment id
        result = self.runner.invoke(container_cli.container, ['status', experiment.id])
        self.assertEqual(result.exit_code, 0)
        self.assertIn(normalize_path(f"{self.platform.job_directory}/{experiment.parent_id}/{experiment.id}"),
                      mock_console.call_args_list[0].args[0])
        self.assertIn('Simulation Count', mock_console.call_args_list[1][0][0])
        self.assertIn('SUCCEEDED', mock_console.call_args_list[2][0][0])
        self.assertIn('FAILED', mock_console.call_args_list[3][0][0])
        self.assertIn('RUNNING', mock_console.call_args_list[4][0][0])
        self.assertIn('PENDING', mock_console.call_args_list[5][0][0])
        # test status with simulation id
        with mock.patch('rich.console.Console.print') as mock_console_sim:
            result = self.runner.invoke(container_cli.container, ['status', experiment.simulations[0].id])
            self.assertIn(f'SIMULATION {experiment.simulations[0].id} is ',
                          mock_console_sim.call_args_list[0][0][0])
        # clean up container
        result = self.runner.invoke(container_cli.container, ['stop-container', self.platform.container_id], '--remove')
        self.assertEqual(result.exit_code, 0)

    def test_status_help(self):
        result = self.runner.invoke(container_cli.container, ['status', "--help"])
        expected_help = ('Usage: container status [OPTIONS] ITEM_ID\n'
                         '\n'
                         '  Check the status of an Experiment/Simulation.\n'
                         '\n'
                         '  Arguments:\n'
                         '\n'
                         '    ITEM_ID: Experiment/Simulation ID or Job ID\n'
                         '\n'
                         'Options:\n'
                         '  -c, --container_id TEXT   Container Id\n'
                         '  -l, --limit INTEGER       Max number of simulations to show\n'
                         '  --verbose / --no-verbose  Display with working directory or not\n'
                         '  --help                    Show this message and exit.\n')
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, expected_help)


if __name__ == '__main__':
    unittest.main()
