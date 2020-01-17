import os
from unittest import TestCase
import pytest
from idmtools_models.r.r_task import RTask, JSONConfiguredRTask
from idmtools_test import COMMON_INPUT_PATH


# TODO Point to actual R model in test files
# It is ok at moment since this is not running model

@pytest.mark.tasks
class TestRTask(TestCase):

    def test_simple_model(self):
        fpath = os.path.join(COMMON_INPUT_PATH, "Rscript", "model1.py")
        task = RTask(script_name=fpath, image_name='r-base:3.6.1')
        task.gather_assets()

        self.assertEqual(str(task.command), f'Rscript ./Assets/model1.py')
        self.assertEqual(len(task.assets.assets), 1)
        self.assertEqual(task.assets.assets[0].absolute_path, fpath)

    def test_json_r_argument(self):
        fpath = os.path.join(COMMON_INPUT_PATH, "Rscript", "model1.py")
        task = JSONConfiguredRTask(script_name=fpath, image_name='r-base:3.6.1')
        task.gather_assets()

        self.assertEqual(str(task.command), f'Rscript ./Assets/model1.py --config config.json')
        self.assertEqual(len(task.assets.assets), 2)
        self.assertEqual(task.assets.assets[0].absolute_path, fpath)
        self.assertEqual(task.assets.assets[1].filename, 'config.json')

    def test_json_r_static_filename_no_argument(self):
        fpath = os.path.join(COMMON_INPUT_PATH, "Rscript", "model1.py")
        task = JSONConfiguredRTask(script_name=fpath, configfile_argument=None, image_name='r-base:3.6.1')
        task.gather_assets()

        self.assertEqual(str(task.command), f'Rscript ./Assets/model1.py')
        self.assertEqual(len(task.assets.assets), 2)
        self.assertEqual(task.assets.assets[0].absolute_path, fpath)
        self.assertEqual(task.assets.assets[1].filename, 'config.json')

    def test_different_r_path(self):
        fpath = os.path.join(COMMON_INPUT_PATH, "Rscript", "model1.py")
        task = JSONConfiguredRTask(script_name=fpath, configfile_argument=None, image_name='r-base:3.6.1',
                                   r_path='/usr/custom/Rscript')
        task.gather_assets()

        self.assertEqual(str(task.command), f'/usr/custom/Rscript ./Assets/model1.py')
