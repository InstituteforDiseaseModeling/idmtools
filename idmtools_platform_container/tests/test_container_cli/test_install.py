import os
import sys
from time import sleep
from unittest.mock import patch
import pytest
import idmtools_platform_container.cli.container as container_cli
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from test_base import TestContainerPlatformCliBase


@pytest.mark.serial
class TestContainerPlatformInstallCli(TestContainerPlatformCliBase):

    @patch('rich.console.Console.print')
    def test_install(self, mock_console):
        command = "sleep 100"
        task = CommandTask(command=command)
        experiment = Experiment.from_task(task, name="run_command")
        experiment.run(wait_until_done=False)
        sleep(1)
        result = self.runner.invoke(container_cli.container, ['install', 'astor', '-c', self.platform.container_id])
        # verify that the package was installed with container packages cli
        result = self.runner.invoke(container_cli.container, ['packages', self.platform.container_id])
        self.assertIn('astor', mock_console.call_args_list[1][0][0])
        # clean up container
        result = self.runner.invoke(container_cli.container, ['stop-container', self.platform.container_id], '--remove')
        self.assertEqual(result.exit_code, 0)

    def test_install_help(self):
        result = self.runner.invoke(container_cli.container, ['install', "--help"])
        expected_help = ('Usage: container install [OPTIONS] PACKAGE\n'
                         '\n'
                         '  pip install a package on a container.\n'
                         '\n'
                         '  Arguments:\n'
                         '\n'
                         '    PACKAGE: package to be installed\n'
                         '\n'
                         'Options:\n'
                         '  -c, --container-id TEXT     Container ID\n'
                         '  -i, --index-url TEXT        index-url for pip install\n'
                         '  -e, --extra-index-url TEXT  extra-index-url for pip install\n'
                         '  --help                      Show this message and exit.\n')
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, expected_help)