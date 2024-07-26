import os
import sys
from time import sleep
from unittest.mock import patch
import pytest
import idmtools_platform_container.cli.container as container_cli
from idmtools.core import ItemType
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
from idmtools_platform_container.utils.general import normalize_path

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from test_base import TestContainerPlatformCliBase


@pytest.mark.serial
class TestContainerPlatformGetDetailCli(TestContainerPlatformCliBase):

    @patch('rich.console.Console.print')
    def test_get_details(self, mock_console):
        command = "sleep 100"
        task = CommandTask(command=command)
        experiment = Experiment.from_task(task, name="run_command")
        experiment.run(wait_until_done=False)
        sleep(1)
        result = self.runner.invoke(container_cli.container, ['get-detail', experiment.id])
        self.assertEqual(result.exit_code, 0)
        self.assertIn(f'"JOB_DIRECTORY": "{normalize_path(self.job_directory)}",',
                      mock_console.call_args_list[0].args[0].text)
        self.assertIn(f'"SUITE_ID": "{experiment.parent_id}",',
                      mock_console.call_args_list[0].args[0].text)
        exp_dir = self.platform.get_directory_by_id(experiment.id, ItemType.EXPERIMENT)
        self.assertIn(
            f'"EXPERIMENT_DIR": "{normalize_path(exp_dir)}",',
            mock_console.call_args_list[0].args[0].text)
        self.assertIn(f'"EXPERIMENT_NAME": "run_command",',
                      mock_console.call_args_list[0].args[0].text)
        self.assertIn(f'"EXPERIMENT_ID": "{experiment.id}",',
                      mock_console.call_args_list[0].args[0].text)
        self.assertIn(f'"CONTAINER": "{self.platform.container_id}",',
                      mock_console.call_args_list[0].args[0].text)
        self.assertIn(f'"CREATED": ',
                      mock_console.call_args_list[0].args[0].text)
        # clean up container
        result = self.runner.invoke(container_cli.container, ['stop-container', self.platform.container_id], '--remove')
        self.assertEqual(result.exit_code, 0)

    def test_get_detail_help(self):
        result = self.runner.invoke(container_cli.container, ['get-detail', "--help"])
        expected_help = ('Usage: container get-detail [OPTIONS] EXP_ID\n'
                         '\n'
                         '  Retrieve Experiment history.\n'
                         '\n'
                         '  Arguments:\n'
                         '\n'
                         '    EXP_ID: Experiment ID\n'
                         '\n'
                         'Options:\n'
                         '  --help  Show this message and exit.\n')
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, expected_help)
