import os
import sys
from time import sleep
import unittest
from unittest.mock import patch
import pytest
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
import idmtools_platform_container.cli.container as container_cli

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)
from test_base import TestContainerPlatformCliBase
from helper import found_job_id_by_experiment, get_actual_rich_table_values


@pytest.mark.serial
class TestContainerPlatformCancelCli(TestContainerPlatformCliBase):
    @patch('rich.console.Console.print')
    def test_cancel_with_experiment_id(self, mock_console):
        command = "sleep 100"
        task = CommandTask(command=command)
        experiment = Experiment.from_task(task, name="run_command")
        experiment.run(wait_until_done=False)
        sleep(1)
        # test cancel with experiment id
        result = self.runner.invoke(container_cli.container, ['cancel', experiment.id])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Successfully killed EXPERIMENT', mock_console.call_args_list[0].args[0])

    @patch('rich.console.Console.print')
    def test_cancel_with_simulation_id(self, mock_console1):
        command = "python3 Assets/sleep.py"
        task = CommandTask(command=command)
        task.common_assets.add_asset(os.path.join(script_dir, "..", "inputs", "sleep.py"))
        experiment = Experiment.from_task(task, name="run_command")
        experiment.run(wait_until_done=False)
        sleep(1)
        # test cancel with simulation id
        result = self.runner.invoke(container_cli.container, ['cancel', experiment.simulations[0].id])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Successfully killed SIMULATION', mock_console1.call_args_list[0].args[0])

    @patch('rich.console.Console.print')
    def test_cancel_with_experiment_job_id_and_container_id(self, mock_console):
        command = "sleep 100"
        task = CommandTask(command=command)
        experiment = Experiment.from_task(task, name="run_command")
        experiment.run(wait_until_done=False)
        sleep(1)
        result = self.runner.invoke(container_cli.container, ['jobs'])
        self.assertEqual(result.exit_code, 0)
        actual_table = get_actual_rich_table_values(mock_console)
        job_id, container_id = found_job_id_by_experiment(actual_table[1:], experiment.id)
        # test cancel with job_id and container_id
        result = self.runner.invoke(container_cli.container, ['cancel', job_id, '-c', container_id])
        self.assertTrue(f'Successfully killed EXPERIMENT {job_id}', mock_console.call_args[0][0])
        self.assertEqual(result.exit_code, 0)

    @patch('rich.console.Console.print')
    def test_cancel_with_job_id_only(self, mock_console):
        command = "sleep 100"
        task = CommandTask(command=command)
        experiment = Experiment.from_task(task, name="run_command")
        experiment.run(wait_until_done=False)
        sleep(1)
        result = self.runner.invoke(container_cli.container, ['jobs'])
        self.assertEqual(result.exit_code, 0)
        actual_table = get_actual_rich_table_values(mock_console)
        job_id, container_id = found_job_id_by_experiment(actual_table[1:], experiment.id)
        # test cancel with job_id and container_id
        result = self.runner.invoke(container_cli.container, ['cancel', job_id])
        self.assertTrue(f'Successfully killed EXPERIMENT {job_id}', mock_console.call_args[0][0])
        self.assertEqual(result.exit_code, 0)

    def test_cancel_help(self):
        result = self.runner.invoke(container_cli.container, ['cancel', "--help"])
        expected_help = (
            "Usage: container cancel [OPTIONS] ITEM_ID\n"
            "\n"
            "  Cancel an Experiment/Simulation job.\n"
            "\n"
            "  Arguments:\n"
            "\n"
            "    ITEM_ID: Experiment/Simulation ID or Job ID\n"
            "\n"
            "Options:\n"
            "  -c, --container_id TEXT  Container Id\n"
            "  --help                   Show this message and exit.\n"
        )
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, expected_help)


if __name__ == '__main__':
    unittest.main()
