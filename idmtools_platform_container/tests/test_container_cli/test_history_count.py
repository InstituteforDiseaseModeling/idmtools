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


@pytest.mark.serial
@pytest.mark.cli
class TestContainerPlatformHistoryCountCli(TestContainerPlatformCliBase):
    @patch('rich.console.Console.print')
    def test_history_count(self, mock_console):
        # first clear the history
        result = self.runner.invoke(container_cli.container, ['clear-history'])
        self.assertEqual(result.exit_code, 0)
        command = "sleep 100"
        task = CommandTask(command=command)
        experiment = Experiment.from_task(task, name="run_command")
        experiment.run(wait_until_done=False)
        # run another experiment job
        experiment1 = Experiment.from_task(task, name="run_command")
        experiment1.run(wait_until_done=False)
        # test history
        result = self.runner.invoke(container_cli.container, ['history-count'])
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(mock_console.call_args_list[0].args[0] == 2)  # Make sure there are 2 jobs in history
        # clean up container
        result = self.runner.invoke(container_cli.container, ['stop-container', self.platform.container_id], '--remove')
        self.assertEqual(result.exit_code, 0)

    def test_history_count_help(self):
        result = self.runner.invoke(container_cli.container, ['history-count', "--help"])
        expected_help = ('Usage: container history-count [OPTIONS] [CONTAINER_ID]\n'
                         '\n'
                         '  Get the count of count histories.\n'
                         '\n'
                         '  Arguments:\n'
                         '\n'
                         '    CONTAINER_ID: Container ID (optional)\n'
                         '\n'
                         'Options:\n'
                         '  --help  Show this message and exit.\n')
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, expected_help)


if __name__ == '__main__':
    unittest.main()
