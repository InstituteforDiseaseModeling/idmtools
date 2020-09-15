import os
from unittest import TestCase
import pytest
from idmtools_models.r.json_r_task import JSONConfiguredRTask
from idmtools_models.r.r_task import RTask
from idmtools_test import COMMON_INPUT_PATH


@pytest.mark.tasks
class TestRTask(TestCase):

    def validate_common_assets(self, fpath, task):
        """
        Validate common assets on a R task

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
        Validate JSON R task has correct transient assets
        Args:
            task: Task to validate
            config_file_name: Files name the json config should be. Default to config.json
        Returns:

        """
        self.assertEqual(len(task.transient_assets.assets), 1)
        self.assertEqual(task.transient_assets.assets[0].filename, config_file_name)

    def test_simple_model(self):
        fpath = os.path.join(COMMON_INPUT_PATH, "r", "model1.R")
        task = RTask(script_path=fpath, image_name='r-base:3.6.1')
        task.gather_all_assets()

        self.assertEqual(str(task.command), f'Rscript ./Assets/model1.R')
        self.validate_common_assets(fpath, task)

    def test_json_r_argument(self):
        fpath = os.path.join(COMMON_INPUT_PATH, "r", "model1.R")
        task = JSONConfiguredRTask(script_path=fpath, image_name='r-base:3.6.1')
        task.gather_all_assets()

        self.assertEqual(str(task.command), f'Rscript ./Assets/model1.R --config config.json')
        self.validate_common_assets(fpath, task)
        self.validate_json_transient_assets(task)

    def test_json_r_static_filename_no_argument(self):
        fpath = os.path.join(COMMON_INPUT_PATH, "r", "model1.R")
        task = JSONConfiguredRTask(script_path=fpath, configfile_argument=None, image_name='r-base:3.6.1')
        task.gather_all_assets()

        self.assertEqual(str(task.command), f'Rscript ./Assets/model1.R')
        self.validate_common_assets(fpath, task)
        self.validate_json_transient_assets(task)

    def test_different_r_path(self):
        fpath = os.path.join(COMMON_INPUT_PATH, "r", "model1.R")
        task = JSONConfiguredRTask(script_path=fpath, configfile_argument=None, image_name='r-base:3.6.1',
                                   r_path='/usr/custom/Rscript')
        task.gather_all_assets()

        self.assertEqual(str(task.command), f'/usr/custom/Rscript ./Assets/model1.R')
        self.validate_common_assets(fpath, task)
        self.validate_json_transient_assets(task)
