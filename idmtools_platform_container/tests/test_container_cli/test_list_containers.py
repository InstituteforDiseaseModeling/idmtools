import os
import re
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
class TestContainerPlatformListContainersCli(TestContainerPlatformCliBase):
    @patch('rich.console.Console.print')
    def test_list_containers(self, mock_console):
        command = "sleep 100"
        task = CommandTask(command=command)
        experiment = Experiment.from_task(task, name="run_command")
        experiment.run(wait_until_done=False)
        result = self.runner.invoke(container_cli.container, ['list-containers'])
        self.assertEqual(result.exit_code, 0)
        # verify there are at least 1 container show up in result
        expected_result = bool(re.match(r'There are [1-9]\d* container\(s\)\.', mock_console.call_args_list[0].args[0]))
        self.assertTrue(expected_result)
        # clean up by stop the job
        result = self.runner.invoke(container_cli.container, ['stop-container', self.platform.container_id])
        self.assertEqual(result.exit_code, 0)

    def test_list_containers_help(self):
        result = self.runner.invoke(container_cli.container, ['list-containers', "--help"])
        expected_help = ('Usage: container list-containers [OPTIONS]\n'
                         '\n'
                         '  List all available containers.\n'
                         '\n'
                         'Options:\n'
                         '  --all / --no-all  Include stopped containers or not\n'
                         '  --help            Show this message and exit.\n')
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, expected_help)


if __name__ == '__main__':
    unittest.main()
