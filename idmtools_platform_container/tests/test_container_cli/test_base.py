import unittest
import os
import pytest
from click.testing import CliRunner
from idmtools.core.platform_factory import Platform


@pytest.mark.serial
class TestContainerPlatformCliBase(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()
        self.job_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "DEST")
        self.platform = Platform("Container", job_directory=self.job_directory)
