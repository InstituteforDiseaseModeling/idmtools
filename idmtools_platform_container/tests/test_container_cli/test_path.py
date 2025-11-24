import os
import sys
from unittest.mock import patch
import pytest

import idmtools_platform_container.cli.container as container_cli
from idmtools.core import ItemType
from idmtools.entities import Suite
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
from idmtools_platform_container.utils.general import normalize_path

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from test_base import TestContainerPlatformCliBase


@pytest.mark.serial
@pytest.mark.cli
class TestContainerPlatformPathCli(TestContainerPlatformCliBase):

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

    @patch('rich.console.Console.print')
    def test_path_new_no_suite(self, mock_console):
        command = "sleep 100"
        task = CommandTask(command=command)
        experiment = Experiment.from_task(task, name="run_command")
        experiment.run(wait_until_done=False)
        result = self.runner.invoke(container_cli.container, ['path', experiment.id])
        self.assertEqual(result.exit_code, 0)
        # check path
        exp_dir = self.platform.get_directory_by_id(experiment.id, ItemType.EXPERIMENT)
        self.assertIn(normalize_path(normalize_path(exp_dir)),
                      normalize_path(mock_console.call_args.args[0].split(' ')[1]))
        # Test simulation path
        with patch("rich.console.Console.print") as mock_console:
            result = self.runner.invoke(container_cli.container, ['path', experiment.simulations[0].id])
            self.assertEqual(result.exit_code, 0)
            sim_dir = self.platform.get_directory_by_id(experiment.simulations[0].id, ItemType.SIMULATION)
            self.assertIn(normalize_path(normalize_path(sim_dir)),
                          normalize_path(mock_console.call_args.args[0].split(' ')[1]))
        # Test suite path
        with patch("rich.console.Console.print") as mock_console:
            result = self.runner.invoke(container_cli.container, ['path', experiment.parent_id])
            self.assertEqual(result.exit_code, 1)

    @patch('rich.console.Console.print')
    def test_path_new_suite(self, mock_console):
        command = "sleep 100"
        task = CommandTask(command=command)
        experiment = Experiment.from_task(task, name="run_command")
        suite = Suite(name="suite_name")
        suite.add_experiment(experiment)
        # Run via Suite (mirrors your original with-suite behavior)
        experiment.run(platform=self.platform, wait_until_done=False)
        result = self.runner.invoke(container_cli.container, ['path', experiment.id])
        self.assertEqual(result.exit_code, 0)
        # check path
        exp_dir = self.platform.get_directory_by_id(experiment.id, ItemType.EXPERIMENT)
        self.assertIn(normalize_path(normalize_path(exp_dir)),
                      normalize_path(mock_console.call_args.args[0].split(' ')[1]))
        # Test simulation path
        with patch("rich.console.Console.print") as mock_console:
            result = self.runner.invoke(container_cli.container, ['path', experiment.simulations[0].id])
            self.assertEqual(result.exit_code, 0)
            sim_dir = self.platform.get_directory_by_id(experiment.simulations[0].id, ItemType.SIMULATION)
            self.assertIn(normalize_path(normalize_path(sim_dir)),
                          normalize_path(mock_console.call_args.args[0].split(' ')[1]))
        # Test suite path
        with patch("rich.console.Console.print") as mock_console:
            result = self.runner.invoke(container_cli.container, ['path', experiment.parent_id])
            self.assertEqual(result.exit_code, 0)
            suite_dir = self.platform.get_directory_by_id(suite.id, ItemType.SUITE)
            self.assertIn(normalize_path(normalize_path(suite_dir)),
                          normalize_path(mock_console.call_args.args[0].split(' ')[1]))

        # Test invalid path
        with patch("idmtools_platform_file.tools.job_history.logger") as mock_logger:
            result = self.runner.invoke(container_cli.container, ['path', "abc"])
            mock_logger.debug.assert_called_with("Invalid item id: abc")
        # clean up container
        result = self.runner.invoke(container_cli.container, ['stop-container', self.platform.container_id], '--remove')
        self.assertEqual(result.exit_code, 0)
