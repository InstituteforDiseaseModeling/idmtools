import allure
import os

import pytest
from idmtools.assets import AssetCollection
from idmtools.builders import SimulationBuilder
from idmtools.core.experiment_factory import experiment_factory
from idmtools.core.platform_factory import Platform
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools_test.utils.test_platform import TestPlatform


@pytest.mark.smoke
@pytest.mark.serial
@allure.story("Entities")
@allure.story("Plugins")
@allure.suite("idmtools_core")
class TestExperimentFactory(ITestWithPersistence):

    def test_build_python_experiment_from_factory(self):
        test_platform: TestPlatform = Platform('Test')
        experiment = experiment_factory.create("Experiment", tags={"a": "1", "b": 2})
        script_path = os.path.join(COMMON_INPUT_PATH, "compsplatform", "working_model.py")
        from idmtools_test.utils.test_task import TestTask
        ts = TemplatedSimulations(base_task=TestTask())
        builder = SimulationBuilder()
        builder.add_sweep_definition(lambda simulation, value: {"p": value}, range(0, 2))
        ts.add_builder(builder)
        experiment.simulations = ts
        experiment.add_asset(script_path)
        test_platform.run_items(experiment)

        self.assertEqual(len(experiment.simulations), 2)
        self.assertEqual(experiment.assets.assets[0].filename, "working_model.py")
        tag_value = "idmtools_test.utils.test_task.TestTask"
        self.assertEqual(experiment.simulations[0].tags, {'p': 0})
        self.assertEqual(experiment.simulations[1].tags, {'p': 1})
        self.assertEqual(experiment.tags['task_type'], tag_value)

        test_platform.cleanup()

    def test_add_asset_collection_to_experiment(self):
        base_path = os.path.abspath(os.path.join(COMMON_INPUT_PATH, "assets", "collections"))
        experiment = experiment_factory.create("Experiment", tags={"a": "1", "b": 2})
        ac = AssetCollection.from_directory(assets_directory=base_path)
        experiment.add_assets(ac)
        for asset in ac:
            self.assertIn(asset, experiment.assets)
