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
@pytest.mark.cli
class TestContainerPlatformProcessCli(TestContainerPlatformCliBase):

    @patch('rich.console.Console.print')
    def test_ps(self, mock_console):
        command = "sleep 100"
        task = CommandTask(command=command)
        experiment = Experiment.from_task(task, name="run_command")
        experiment.run(wait_until_done=False)
        result = self.runner.invoke(container_cli.container, ['ps', self.platform.container_id])
        self.assertEqual(result.exit_code, 0)
        # check ps
        self.assertIn(f'EXPERIMENT:{experiment.id} batch.sh', mock_console.call_args_list[0].args[0])
        # self.assertIn(
        #     "xargs -d \\n -P 4 -I% bash -c cd $(pwd) && $(pwd)/run_simulation.sh %  1>> stdout.txt 2>> stderr.txt",
        #     mock_console.call_args_list[0].args[0])
        # clean up container
        result = self.runner.invoke(container_cli.container, ['stop-container', self.platform.container_id], '--remove')
        self.assertEqual(result.exit_code, 0)

    def test_ps_help(self):
        result = self.runner.invoke(container_cli.container, ['ps', "--help"])
        expected_help = ('Usage: container ps [OPTIONS] CONTAINER_ID\n'
                         '\n'
                         '  List running processes in a container.\n'
                         '\n'
                         '  Arguments:\n'
                         '\n'
                         '    CONTAINER_ID: Container ID\n'
                         '\n'
                         'Options:\n'
                         '  --help  Show this message and exit.\n')
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, expected_help)
