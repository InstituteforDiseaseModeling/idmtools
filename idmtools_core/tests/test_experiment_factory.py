import os

from idmtools.assets import AssetCollection
from idmtools.builders import SimulationBuilder, StandAloneSimulationsBuilder
from idmtools.core.experiment_factory import experiment_factory
from idmtools.core.platform_factory import Platform
from idmtools.managers import ExperimentManager
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.decorators import windows_only
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools_test.utils.test_platform import TestPlatform


class TestExperimentFactory(ITestWithPersistence):

    def test_build_python_experiment_from_factory(self):
        test_platform: TestPlatform = Platform('Test')
        experiment = experiment_factory.create("PythonExperiment", tags={"a": "1", "b": 2})
        experiment.model_path = os.path.join(COMMON_INPUT_PATH, "compsplatform", "working_model.py")
        builder = SimulationBuilder()
        builder.add_sweep_definition(lambda simulation, value: {"p": value}, range(0, 2))
        experiment.builder = builder

        em = ExperimentManager(experiment=experiment, platform=test_platform)
        em.run()

        self.assertEqual(len(em.experiment.simulations), 2)
        self.assertEqual(em.experiment.assets.assets[0].filename, "working_model.py")
        self.assertEqual(em.experiment.simulations[0].tags, {'p': 0})
        self.assertEqual(em.experiment.simulations[1].tags, {'p': 1})

        test_platform.cleanup()

    def test_add_asset_collection_to_experiment(self):
        base_path = os.path.abspath(os.path.join(COMMON_INPUT_PATH, "assets", "collections"))
        experiment = experiment_factory.create("PythonExperiment", tags={"a": "1", "b": 2})
        ac = AssetCollection.from_directory(assets_directory=base_path)
        experiment.add_assets(ac)
        for asset in ac:
            self.assertIn(asset, experiment.assets)

    @windows_only
    def test_build_emod_experiment_from_factory(self):
        test_platform = Platform('Test')
        experiment = experiment_factory.create("EMODExperiment", tags={"a": "1", "b": 2},
                                               eradication_path=os.path.join(COMMON_INPUT_PATH, "emod"))
        experiment.base_simulation.load_files(config_path=os.path.join(COMMON_INPUT_PATH, "files", "config.json"),
                                              campaign_path=os.path.join(COMMON_INPUT_PATH, "files", "campaign.json"))
        experiment.demographics.add_demographics_from_file(
            os.path.join(COMMON_INPUT_PATH, "files", "demographics.json"))

        b = StandAloneSimulationsBuilder()
        for i in range(20):
            sim = experiment.simulation()
            sim.set_parameter("Enable_Immunity", 0)
            b.add_simulation(sim)
        experiment.builder = b

        em = ExperimentManager(experiment=experiment, platform=test_platform)
        em.run()

        self.assertEqual(len(em.experiment.simulations), 20)
        self.assertEqual(em.experiment.tags, {'a': '1', 'b': 2,
                                              'type': 'idmtools_model_emod.emod_experiment.EMODExperiment'})
        test_platform.cleanup()

