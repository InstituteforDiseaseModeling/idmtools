import os
import sys
import unittest
from unittest.mock import patch
from click.testing import CliRunner
import pytest
import idmtools_platform_container.cli.container as container_cli
from idmtools.core.platform_factory import Platform
from idmtools_platform_container.container_operations.docker_operations import stop_container

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


@pytest.mark.serial
class TestContainerPlatformVolumeCli(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()
        self.job_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "DEST")
        self.platform = Platform("Container", job_directory=self.job_directory)

    @classmethod
    def tearDownClass(cls):
        try:
            stop_container(cls.platform.container_id, remove=True)
        except Exception as e:
            pass
    @patch('rich.console.Console.print')
    def test_volume(self, mock_console):
        result = self.runner.invoke(container_cli.container, ['volume'])
        self.assertIn('Job history volume: ', mock_console.call_args_list[0][0][0])

    def test_volume_help(self):
        result = self.runner.invoke(container_cli.container, ['volume', "--help"])
        expected_help = ('Usage: container volume [OPTIONS]\n'
                        '\n'
                        '  Check the history volume.\n'
                        '\n'
                        'Options:\n'
                        '  --help  Show this message and exit.\n')
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, expected_help)