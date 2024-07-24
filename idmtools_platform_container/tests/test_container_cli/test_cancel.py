import os
import sys
import unittest
from unittest.mock import patch
import pytest
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
import idmtools_platform_container.cli.container as container_cli
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
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
        # test cancel with experiment id
        result = self.runner.invoke(container_cli.container, ['cancel', experiment.id])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Successfully killed EXPERIMENT', mock_console.call_args_list[0].args[0])

    @patch('rich.console.Console.print')
    def test_cancel_with_experiment_job_id_and_container_id(self, mock_console):
        command = "sleep 100"
        task = CommandTask(command=command)
        experiment = Experiment.from_task(task, name="run_command")
        experiment.run(wait_until_done=False)
        result = self.runner.invoke(container_cli.container, ['jobs'])
        self.assertEqual(result.exit_code, 0)
        actual_table = get_actual_rich_table_values(mock_console)
        job_id, container_id = found_job_id_by_experiment(actual_table, experiment.id)
        # test cancel with job_id and container_id
        result = self.runner.invoke(container_cli.container, ['cancel', job_id, '-c', container_id])
        self.assertTrue(f'Successfully killed EXPERIMENT {job_id}', mock_console.call_args[0][0])
        self.assertEqual(result.exit_code, 0)
        # clean up container
        result = self.runner.invoke(container_cli.container, ['stop-container', self.platform.container_id], '--remove')
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
