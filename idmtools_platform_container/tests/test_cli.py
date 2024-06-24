import json
import os
import shutil
import unittest
from pathlib import Path
from unittest.mock import patch
from click.testing import CliRunner
import idmtools_platform_file.cli.file as file_cli
from idmtools.core import EntityStatus, ItemType
from idmtools.core.platform_factory import Platform
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment


class TestContainerPlatformCli(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.job_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "DEST")
        self.platform = Platform("Container", job_directory=self.job_directory)
        command = "ls -lat"
        task = CommandTask(command=command)
        self.experiment = Experiment.from_task(task, name="run_command")
        self.experiment.run(wait_until_done=True)
        self.assertEqual(self.experiment.status, EntityStatus.SUCCEEDED)

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(os.path.join(os.path.dirname(os.path.abspath(__file__)), "DEST"))

    # Test cli: test experiment or simulation status report
    # idmtools file job_directory status-report --suite-id <suite_id>
    @patch('idmtools_platform_file.tools.status_report.status_report.user_logger')
    def test_status_report(self, mock_user_logger):
        result = self.runner.invoke(file_cli.file,
                                    [self.job_directory, 'status-report', '--suite-id', self.experiment.parent_id])
        self.assertEqual(result.exit_code, 0)
        actual_messages = [call[0][0] for call in mock_user_logger.info.call_args_list]

        # verify there are total 18 lines for this cli command
        self.assertEqual(mock_user_logger.info.call_count, 18)

        # verify first 3 lines as expected messages
        expected_messages_first_3_lines = [
            f"{'suite: '.ljust(20)} {self.experiment.parent_id}",
            f"{'experiment: '.ljust(20)} {self.experiment.id}",
            f"{'job directory: '.ljust(20)} {self.job_directory}",
        ]
        self.assertEqual(actual_messages[:3], expected_messages_first_3_lines)

        # verify last 8 lines as expected messages
        expected_messages_last_few_lines = [
            f"{'status filter: '.ljust(20)} ('0', '-1', '100')",
            f"{'sim filter: '.ljust(20)} None",
            f"{'verbose: '.ljust(20)} True",
            f"{'display: '.ljust(20)} True",
            f"{'Simulation Count: '.ljust(20)} {self.experiment.simulation_count}",
            f"{'Match Count: '.ljust(20)} 1 ({{'0': 1}})",
            f"{'Not Running Count: '.ljust(20)} 0",
            "\nExperiment Status: SUCCEEDED"
        ]
        self.assertEqual(actual_messages[-8:], expected_messages_last_few_lines)

    # Test cli: get latest experiment info
    # idmtools file job_directory get-latest
    @patch('idmtools_platform_file.cli.file.user_logger')
    def test_get_latest(self, mock_user_logger):
        result = self.runner.invoke(file_cli.file, [self.job_directory, 'get-latest'])
        self.assertEqual(result.exit_code, 0)
        exp_dir = str(self.platform.get_directory_by_id(self.experiment.id, ItemType.EXPERIMENT))
        expected_dict = dict(suite_id=self.experiment.parent_id, experiment_id=self.experiment.id,
                             experiment_directory=exp_dir,
                             job_directory=self.job_directory)
        actual_messages = [call[0][0] for call in mock_user_logger.info.call_args_list]
        self.assertEqual(actual_messages[0], json.dumps(expected_dict, indent=3))

    # Test cli: Get simulation/experiment's status
    # idmtools file job_directory status --exp-id <exp_id>
    @patch('idmtools_platform_file.tools.status_report.utils.user_logger')
    def test_status(self, mock_user_logger):
        result = self.runner.invoke(file_cli.file, [self.job_directory, 'status', '--exp-id', self.experiment.id])
        self.assertEqual(result.exit_code, 0)
        actual_messages = [call[0][0] for call in mock_user_logger.info.call_args_list]
        exp_dir = str(self.platform.get_directory_by_id(self.experiment.id, ItemType.EXPERIMENT))
        expected_messages = [
            f"\nExperiment Directory: \n{exp_dir}",
            "\nSimulation Count:    1\n",
            "SUCCEEDED (1)",
            "FAILED (0)",
            "RUNNING (0)",
            "PENDING (0)",
            f"\nExperiment Status: SUCCEEDED\n"]
        self.assertEqual(actual_messages, expected_messages)

    # Test cli: get status of experiment/simulation
    # idmtools file job_directory get-status --exp-id <exp_id>
    @patch('idmtools_platform_file.cli.file.user_logger')
    def test_get_status(self, mock_user_logger):
        result = self.runner.invoke(file_cli.file, [self.job_directory, 'get-status', '--exp-id', self.experiment.id])
        self.assertEqual(result.exit_code, 0)
        mock_user_logger.info.assert_called_with("SUCCEEDED")

    # Test cli: get path of experiment/simulation
    # idmtools file job_directory get-path --exp-id <exp_id>
    @patch('idmtools_platform_file.cli.file.user_logger')
    def test_get_path(self, mock_user_logger):
        result = self.runner.invoke(file_cli.file, [self.job_directory, 'get-path', '--exp-id', self.experiment.id])
        self.assertEqual(result.exit_code, 0)
        exp_dir = str(self.platform.get_directory_by_id(self.experiment.id, ItemType.EXPERIMENT))
        mock_user_logger.info.assert_called_with(Path(exp_dir))


if __name__ == '__main__':
    unittest.main()
