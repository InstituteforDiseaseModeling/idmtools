import os
from unittest import TestCase

import pytest

from idmtools_test.utils.utils import test_example_folder

examples_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'examples'))
analyzers_folder = os.path.join(examples_folder, 'analyzers')


@pytest.mark.example
class TestAnalyzersExample(TestCase):
    def test_analyzers_directory(self):
        test_example_folder(self, analyzers_folder)

