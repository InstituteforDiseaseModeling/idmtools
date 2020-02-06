import os
from unittest import TestCase

import pytest

from idmtools_test.utils.utils import test_example_folder

examples_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'examples'))
builders_folder = os.path.join(examples_folder, 'builders')


@pytest.mark.example
class TestBuildersExample(TestCase):
    def test_builders_directory(self):
        test_example_folder(self, builders_folder)
