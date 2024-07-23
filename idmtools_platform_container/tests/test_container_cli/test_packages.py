import os
import sys
from unittest.mock import patch
import pytest
import idmtools_platform_container.cli.container as container_cli
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from test_base import TestContainerPlatformCliBase


@pytest.mark.serial
class TestContainerPlatformPackagesCli(TestContainerPlatformCliBase):

    @patch('rich.console.Console.print')
    def test_packages(self, mock_console):
        command = "sleep 100"
        task = CommandTask(command=command)
        experiment = Experiment.from_task(task, name="run_command")
        experiment.run(wait_until_done=False)
        result = self.runner.invoke(container_cli.container, ['packages', self.platform.container_id])
        self.assertIn('Package             Version', mock_console.call_args_list[0][0][0])
        self.assertIn('numpy', mock_console.call_args_list[0][0][0])
        # clean up by stop the job
        result = self.runner.invoke(container_cli.container, ['stop-container', self.platform.container_id], '--remove')
        self.assertEqual(result.exit_code, 0)

    def test_packages_help(self):
        result = self.runner.invoke(container_cli.container, ['packages', "--help"])
        expected_help = ('Usage: container packages [OPTIONS] CONTAINER_ID\n'
                        '\n'
                        '  List packages installed on a container.\n'
                        '\n'
                        '  Arguments:\n'
                        '\n'
                        '    CONTAINER_ID: Container ID\n'
                        '\n'
                        'Options:\n'
                        '  --help  Show this message and exit.\n')
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, expected_help)