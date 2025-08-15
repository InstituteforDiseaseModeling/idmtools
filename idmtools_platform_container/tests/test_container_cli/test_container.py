import os
import sys
import pytest
import idmtools_platform_container.cli.container as container_cli

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from test_base import TestContainerPlatformCliBase

@pytest.mark.serial
@pytest.mark.cli
class TestContainerPlatformCliContainer(TestContainerPlatformCliBase):

    def test_container_help(self):
        result = self.runner.invoke(container_cli.container, ["--help"])
        expected_help = ('Usage: container [OPTIONS] COMMAND [ARGS]...\n'
                         '\n'
                         '  Container Platform CLI commands.\n'
                         '\n'
                         '  Args:     all: Bool, show all commands\n'
                         '\n'
                         '  Returns:     None\n'
                         '\n'
                         'Options:\n'
                         '  --all   Show all commands\n'
                         '  --help  Show this message and exit.\n'
                         '\n'
                         'Commands:\n'
                         '  cancel   Cancel an Experiment/Simulation job.\n'
                         '  history  View the job history.\n'
                         '  jobs     List running Experiment/Simulation jobs.\n'
                         '  status   Check the status of an Experiment/Simulation.\n'
                         )
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, expected_help)

    def test_container_help_all(self):
        result = self.runner.invoke(container_cli.container, ["--all", "--help"])
        expected_help_all = ('Usage: container [OPTIONS] COMMAND [ARGS]...\n'
                             '\n'
                             '  Container Platform CLI commands.\n'
                             '\n'
                             '  Args:     all: Bool, show all commands\n'
                             '\n'
                             '  Returns:     None\n'
                             '\n'
                             'Options:\n'
                             '  --all   Show all commands\n'
                             '  --help  Show this message and exit.\n'
                             '\n'
                             'Commands:\n'
                             '  cancel            Cancel an Experiment/Simulation job.\n'
                             '  clear-history     Clear the job history.\n'
                             '  clear-results     Clear job results files and folders.\n'
                             '  get-detail        Retrieve Experiment history.\n'
                             '  history           View the job history.\n'
                             '  history-count     Get the count of count histories.\n'
                             '  inspect           Inspect a container.\n'
                             '  install           pip install a package on a container.\n'
                             '  is-running        Check if an Experiment/Simulation is running.\n'
                             '  jobs              List running Experiment/Simulation jobs.\n'
                             '  list-containers   List all available containers.\n'
                             '  packages          List packages installed on a container.\n'
                             '  path              Locate Suite/Experiment/Simulation file directory.\n'
                             '  ps                List running processes in a container.\n'
                             '  remove-container  Remove stopped containers.\n'
                             '  status            Check the status of an Experiment/Simulation.\n'
                             '  stop-container    Stop running container(s).\n'
                             '  sync-history      Sync the file system with job history.\n'
                             '  verify-docker     Verify the Docker environment.\n'
                             '  volume            Check the history volume.\n'
                             )
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, expected_help_all)
