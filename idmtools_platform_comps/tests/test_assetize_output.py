import os

import pytest
import unittest

from idmtools.core import EntityStatus
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_platform_comps.utils.assetize_output.assetize_output import AssetizeOutput
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.test_task import TestTask


@pytest.mark.comps
class TestAssetizeOutput(unittest.TestCase):
    @pytest.mark.smoke
    def test_experiment_can_be_watched(self):
        e = Experiment.from_task(task=TestTask())
        ao = AssetizeOutput()
        ao.run_after(e)
        self.assertEqual(1, len(ao.related_experiments))
        self.assertEqual(ao.related_experiments[0], e)

    @pytest.mark.smoke
    def test_experiment_precreate_fails_if_not_all_items_created(self):
        e = Experiment.from_task(task=TestTask())
        e2 = Experiment.from_task(task=TestTask())

        e.simulations[0].status = EntityStatus.CREATED
        ao = AssetizeOutput()
        ao.run_after([e, e2])
        self.assertEqual(2, len(ao.related_experiments))
        with self.assertRaises(ValueError) as er:
            ao.pre_creation(None)
        self.assertEqual(er.exception.args[0], "Ensure all dependent items are in a create state before attempting to create the Assetize Watcher")

    @pytest.mark.smoke
    def test_experiment_precreate_fails_if_no_watched_items(self):
        ao = AssetizeOutput()
        self.assertEqual(0, len(ao.related_experiments))
        with self.assertRaises(ValueError) as er:
            ao.pre_creation(None)
        self.assertEqual(er.exception.args[0], "You must specify at least one item to watch")

    @pytest.mark.smoke
    def test_experiment_default_pattern_if_none_specified(self):
        e = Experiment.from_task(task=TestTask())
        e.simulations[0].status = EntityStatus.CREATED
        ao = AssetizeOutput()
        ao.run_after(e)
        self.assertEqual(1, len(ao.related_experiments))
        self.assertEqual(ao.related_experiments[0], e)
        ao.pre_creation(None)
        self.assertEqual(1, len(ao.file_patterns))
        self.assertEqual("**", ao.file_patterns[0])

    def test_comps_simple(self):
        platform = Platform("COMPS2")
        task = JSONConfiguredPythonTask(script_path=os.path.join(COMMON_INPUT_PATH, "python", "model1.py"), parameters=dict(a=1))
        e = Experiment.from_task(task=task)
        ao = AssetizeOutput()
        ao.run_after(e)
        e.run(wait_until_done=True)
        ao.run(wait_on_done=True)

        self.assertTrue(e.succeeded)
