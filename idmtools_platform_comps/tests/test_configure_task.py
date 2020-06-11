import unittest
import pytest
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools_models.json_configured_task import JSONConfiguredTask


@pytest.mark.comps
class TestExperimentOperations(unittest.TestCase):
    def test_reload_from_simulation_task1(self):
        with Platform("COMPS2") as p:
            command: str = "python -m json.tool --config my_config.json"
            config_file_name: str = 'my_config.json'

            task = JSONConfiguredTask(command=command, config_file_name=config_file_name, parameters=dict(a=1, b=2, c=3))
            experiment = Experiment.from_task(task=task, name="Test")
            experiment.run(True)
            self.assertTrue(experiment.succeeded)