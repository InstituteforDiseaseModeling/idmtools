import unittest
import os
import pytest
from click.testing import CliRunner
from idmtools.core.platform_factory import Platform


@pytest.mark.serial
class TestContainerPlatformCliBase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.runner = CliRunner()
        cls.job_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "DEST")
        cls.platform = Platform("Container", job_directory=cls.job_directory)
