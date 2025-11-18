import os
from unittest import TestCase
import pytest
from idmtools_test.utils.utils import test_example_folder

examples_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'examples'))
python_model = os.path.join(examples_folder, 'python_model')


@pytest.mark.example
class TestPythonModelDirectory(TestCase):
    def test_python_model_directory(self):
        test_example_folder(self, python_model)

