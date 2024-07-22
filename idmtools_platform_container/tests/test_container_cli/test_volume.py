import os
import sys
from unittest.mock import patch
import pytest
import idmtools_platform_container.cli.container as container_cli
from .test_base import TestContainerPlatformCliBase
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


@pytest.mark.serial
class TestContainerPlatformVolumeCli(TestContainerPlatformCliBase):

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