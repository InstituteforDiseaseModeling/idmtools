import pytest
import unittest
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