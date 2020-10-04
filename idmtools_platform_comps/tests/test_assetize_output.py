import pytest
import unittest

from idmtools.core import EntityStatus
from idmtools.entities.experiment import Experiment
from idmtools_platform_comps.utils.assetize_output.assetize_output import AssetizeOutput
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