import os
import sys
from unittest.mock import patch
import pytest
import idmtools_platform_container.cli.container as container_cli
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from test_base import TestContainerPlatformCliBase


@pytest.mark.serial
@pytest.mark.cli
class TestContainerPlatformVerifyDockerCli(TestContainerPlatformCliBase):

    @patch('rich.console.Console.print')
    def test_verify_docker(self, mock_console):
        result = self.runner.invoke(container_cli.container, ['verify-docker'])
        self.assertIn('Docker version ', mock_console.call_args_list[0][0][0])

    def test_verify_docker_help(self):
        result = self.runner.invoke(container_cli.container, ['verify-docker', "--help"])
        expected_help = ('Usage: container verify-docker [OPTIONS]\n'
                        '\n'
                        '  Verify the Docker environment.\n'
                        '\n'
                        'Options:\n'
                        '  --help  Show this message and exit.\n')
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, expected_help)