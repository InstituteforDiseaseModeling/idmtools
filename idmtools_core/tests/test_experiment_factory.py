import os

from idmtools.builders import ExperimentBuilder, StandAloneSimulationsBuilder
from idmtools.core import experiment_factory
from idmtools.managers import ExperimentManager
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.ITestWithPersistence import ITestWithPersistence
from idmtools_test.utils.TestPlatform import TestPlatform
from idmtools_test.utils.TstExperiment import TstExperiment


class TestExperimentFactory(ITestWithPersistence):

    def test_build_python_experiment_from_factory(self):
        experiment = experiment_factory.create("PythonExperiment", tags={"a": "1", "b": 2})
        experiment.model_path = os.path.join(COMMON_INPUT_PATH, "compsplatform", "working_model.py")
        test_platform = TestPlatform()
        builder = ExperimentBuilder()
        builder.add_sweep_definition(lambda simulation, value: {"p": value}, range(0, 2))
        experiment.builder = builder

        em = ExperimentManager(experiment=experiment, platform=test_platform)
        em.run()
        self.assertEqual(len(em.experiment.simulations), 2)
        self.assertEqual(em.experiment.assets.assets[0].filename, "working_model.py")
        self.assertEqual(em.experiment.simulations[0].tags, {'p': 0})
        self.assertEqual(em.experiment.simulations[1].tags, {'p': 1})

    def test_build_dtk_experiment_from_factory(self):
        experiment = experiment_factory.create("DTKExperiment", tags={"a": "1", "b": 2},
                                               eradication_path=os.path.join(COMMON_INPUT_PATH, "dtk"))
        experiment.load_files(config_path=os.path.join(COMMON_INPUT_PATH, "files", "config.json"),
                              campaign_path=os.path.join(COMMON_INPUT_PATH, "files", "campaign.json"),
                              demographics_paths=os.path.join(COMMON_INPUT_PATH, "files", "demographics.json"))

        test_platform = TestPlatform()
        b = StandAloneSimulationsBuilder()

        for i in range(20):
            sim = experiment.simulation()
            sim.set_parameter("Enable_Immunity", 0)
            b.add_simulation(sim)

            experiment.builder = b
        em = ExperimentManager(platform=test_platform, experiment=experiment)

        em.run()
        self.assertEqual(len(em.experiment.simulations), 20)
        self.assertEqual(em.experiment.tags, {'a': '1', 'b': 2, 'type': 'idmtools_model_dtk.DTKExperiment'})

    def test_build_test_experiment_from_factory(self):
        test_experiment = TstExperiment()
        test_experiment.tags = {"a": "1", "b": 2}
        test_experiment.pre_creation()

        experiment = experiment_factory.create(test_experiment.tags.get("type"), tags=test_experiment.tags)
        self.assertIsNotNone(experiment.uid)
        self.assertEqual(experiment.tags, {'a': '1', 'b': 2, 'type': 'idmtools_test.utils.TstExperiment'})
