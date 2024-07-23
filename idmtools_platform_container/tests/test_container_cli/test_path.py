import os
import sys
from unittest.mock import patch

import pytest
import idmtools_platform_container.cli.container as container_cli
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
from idmtools_platform_container.utils.general import normalize_path

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from test_base import TestContainerPlatformCliBase


@pytest.mark.serial
class TestContainerPlatformPathCli(TestContainerPlatformCliBase):

    @patch('rich.console.Console.print')
    def test_path(self, mock_console):
        command = "sleep 100"
        task = CommandTask(command=command)
        experiment = Experiment.from_task(task, name="run_command")
        experiment.run(wait_until_done=False)
        result = self.runner.invoke(container_cli.container, ['path', experiment.id])
        self.assertEqual(result.exit_code, 0)
        # check path

        self.assertIn(normalize_path(f'{self.platform.job_directory}/{experiment.parent_id}/{experiment.id}'),
                      normalize_path(mock_console.call_args.args[0].split(' ')[1]))
        # clean up by stop the job
        result = self.runner.invoke(container_cli.container, ['stop-container', self.platform.container_id], '--remove')
        self.assertEqual(result.exit_code, 0)

    def test_path_help(self):
        result = self.runner.invoke(container_cli.container, ['path', "--help"])
        expected_help = ('Usage: container path [OPTIONS] ITEM_ID\n'
                         '\n'
                         '  Locate Suite/Experiment/Simulation file directory.\n'
                         '\n'
                         '  Arguments:\n'
                         '\n'
                         '    ITEM_ID: Suite/Experiment/Simulation ID\n'
                         '\n'
                         'Options:\n'
                         '  --help  Show this message and exit.\n')
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, expected_help)
