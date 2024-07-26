import os
import re
import sys
import unittest
from unittest.mock import patch
import pytest
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
import idmtools_platform_container.cli.container as container_cli
from idmtools_platform_container.container_platform import ContainerPlatform

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from test_base import TestContainerPlatformCliBase
from helper import get_actual_rich_table_values, cleaned_str

upper_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(upper_dir)
from utils import delete_containers_by_image_prefix


@pytest.mark.serial
class TestContainerPlatformListContainersCli(TestContainerPlatformCliBase):
    def setUp(self):
        super(TestContainerPlatformListContainersCli, self).setUpClass()
        delete_containers_by_image_prefix(self.platform.docker_image)

    @patch('rich.console.Console.print')
    def test_list_containers(self, mock_console):
        command = "sleep 100"
        task = CommandTask(command=command)
        experiment = Experiment.from_task(task, name="run_command")
        experiment.run(wait_until_done=False, platform=self.platform)
        result = self.runner.invoke(container_cli.container, ['list-containers'])
        self.assertEqual(result.exit_code, 0)
        # verify there are at least 1 container show up in result
        expected_result = bool(re.match(r'There are 1 container\(s\)\.', mock_console.call_args_list[0].args[0]))
        self.assertTrue(expected_result)
        table = get_actual_rich_table_values(mock_console)
        expected_head = ["Container ID", "Image", "Status", "Created", "Started", "Name"]
        self.assertEqual(table[0], expected_head)
        self.assertEqual(self.platform.container_id, table[1][0])
        self.assertEqual(self.platform.docker_image, table[1][1])
        self.assertIn("running", cleaned_str(table[1][2]))
        match_created_time = re.match(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$', table[1][3])
        match_started_time = re.match(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$', table[1][4])
        self.assertTrue(match_created_time)
        self.assertTrue(match_started_time)
        # clean up container
        result = self.runner.invoke(container_cli.container, ['stop-container', self.platform.container_id])
        self.assertEqual(result.exit_code, 0)

    @patch('rich.console.Console.print')
    def test_list_containers_all(self, mock_console):
        # create first job then stop it
        platform1 = ContainerPlatform(job_directory=self.job_directory)
        command = "sleep 100"
        task = CommandTask(command=command)
        experiment = Experiment.from_task(task, name="run_command")
        experiment.run(wait_until_done=False, platform=platform1)
        # stop container
        result = self.runner.invoke(container_cli.container, ['stop-container', platform1.container_id])
        self.assertEqual(result.exit_code, 0)
        # create another job
        platform2 = ContainerPlatform(job_directory=self.job_directory, new_container=True)
        command = "sleep 100"
        task = CommandTask(command=command)
        experiment2 = Experiment.from_task(task, name="run_command")
        experiment2.run(wait_until_done=False, platform=platform2)
        with patch('rich.console.Console.print') as mock_console:
            result = self.runner.invoke(container_cli.container, ['list-containers', '--all'])
            self.assertEqual(result.exit_code, 0)
            # verify there are at least 2 container show up in result
            expected_result = bool(
                re.match(r'There are [1-9]\d* container\(s\)\.', mock_console.call_args_list[0].args[0]))
            self.assertTrue(expected_result)

        # clean up container
        result = self.runner.invoke(container_cli.container, ['stop-container', platform1.container_id])
        self.assertEqual(result.exit_code, 0)
        # clean up container
        result = self.runner.invoke(container_cli.container, ['stop-container', platform2.container_id])
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
