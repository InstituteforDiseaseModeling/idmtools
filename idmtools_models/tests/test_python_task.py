import os
from unittest import TestCase
import pytest

from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_models.python.python_task import PythonTask
from idmtools_test import COMMON_INPUT_PATH


@pytest.mark.tasks
class TestPythonTask(TestCase):

    def test_simple_model(self):
        fpath = os.path.join(COMMON_INPUT_PATH, "python", "model1.py")
        task = PythonTask(script_name=fpath)
        task.gather_all_assets()

        self.assertEqual(str(task.command), f'python ./Assets/model1.py')
        self.validate_common_assets(fpath, task)

    def validate_common_assets(self, fpath, task):
        """
        Validate common assets on a python model

        Args:
            fpath: Source path to model file
            task: Task object to validate

        Returns:
            None
        """
        self.assertEqual(len(task.common_assets.assets), 1, f'Asset list is: {[str(x) for x in task.common_assets.assets]}')
        self.assertEqual(task.common_assets.assets[0].absolute_path, fpath)

    def validate_json_transient_assets(self, task, config_file_name='config.json'):
        """
        Validate JSON Python task has correct transient assets
        Args:
            task: Task to validate
            config_file_name: Files name the json config should be. Default to config.json
        Returns:

        """
        self.assertEqual(len(task.transient_assets.assets), 1)
        self.assertEqual(task.transient_assets.assets[0].filename, config_file_name)

    def test_json_python_argument(self):
        fpath = os.path.join(COMMON_INPUT_PATH, "python", "model1.py")
        task = JSONConfiguredPythonTask(script_name=fpath)
        task.gather_all_assets()

        self.assertEqual(str(task.command), f'python ./Assets/model1.py --config config.json')
        self.validate_common_assets(fpath, task)
        self.validate_json_transient_assets(task)

    def test_json_python_static_filename_no_argument(self):
        fpath = os.path.join(COMMON_INPUT_PATH, "python", "model1.py")
        # here we test a script that may have no configu
        task = JSONConfiguredPythonTask(script_name=fpath, configfile_argument=None)
        task.gather_all_assets()

        self.assertEqual(str(task.command), f'python ./Assets/model1.py')
        self.validate_common_assets(fpath, task)
        self.validate_json_transient_assets(task)

    def test_different_python_path(self):
        fpath = os.path.join(COMMON_INPUT_PATH, "python", "model1.py")
        task = JSONConfiguredPythonTask(script_name=fpath, configfile_argument=None, python_path='python3.8')
        task.gather_all_assets()

        self.assertEqual(str(task.command), f'python3.8 ./Assets/model1.py')
        self.validate_common_assets(fpath, task)
        self.validate_json_transient_assets(task)
