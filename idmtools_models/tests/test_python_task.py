import os
from unittest import TestCase
import pytest

from idmtools_models.python.python_task import PythonTask, JSONConfiguredPythonTask
from idmtools_test import COMMON_INPUT_PATH


@pytest.mark.tasks
class TestPythonTask(TestCase):

    def test_simple_model(self):
        fpath = os.path.join(COMMON_INPUT_PATH, "python", "model1.py")
        task = PythonTask(script_name=fpath)
        task.gather_assets()

        self.assertEqual(str(task.command), f'python ./Assets/model1.py')
        self.assertEqual(len(task.assets.assets), 1)
        self.assertEqual(task.assets.assets[0].absolute_path, fpath)

    def test_json_python_argument(self):
        fpath = os.path.join(COMMON_INPUT_PATH, "python", "model1.py")
        task = JSONConfiguredPythonTask(script_name=fpath)
        task.gather_assets()

        self.assertEqual(str(task.command), f'python ./Assets/model1.py --config config.json')
        self.assertEqual(len(task.assets.assets), 2)
        self.assertEqual(task.assets.assets[0].absolute_path, fpath)
        self.assertEqual(task.assets.assets[1].filename, 'config.json')

    def test_json_python_static_filename_no_argument(self):
        fpath = os.path.join(COMMON_INPUT_PATH, "python", "model1.py")
        task = JSONConfiguredPythonTask(script_name=fpath, configfile_argument=None)
        task.gather_assets()

        self.assertEqual(str(task.command), f'python ./Assets/model1.py')
        self.assertEqual(len(task.assets.assets), 2)
        self.assertEqual(task.assets.assets[0].absolute_path, fpath)
        self.assertEqual(task.assets.assets[1].filename, 'config.json')

    def test_different_python_path(self):
        fpath = os.path.join(COMMON_INPUT_PATH, "Rscript", "model1.py")
        task = JSONConfiguredPythonTask(script_name=fpath, configfile_argument=None, python_path='python3.8')
        task.gather_assets()

        self.assertEqual(str(task.command), f'python3.8 ./Assets/model1.py')
