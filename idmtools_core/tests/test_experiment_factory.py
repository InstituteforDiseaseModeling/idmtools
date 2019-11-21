import os

from idmtools.builders import ExperimentBuilder, StandAloneSimulationsBuilder
from idmtools.core.model_factory import model_factory
from idmtools.core.platform_factory import Platform
from idmtools.managers import ExperimentManager
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.decorators import windows_only
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools_test.utils.tst_experiment import TstExperiment


class TestExperimentFactory(ITestWithPersistence):

    def test_build_python_experiment_from_factory(self):
        test_platform = Platform('Test')
        experiment = model_factory.create("PythonExperiment", tags={"a": "1", "b": 2})
        experiment.model_path = os.path.join(COMMON_INPUT_PATH, "compsplatform", "working_model.py")
        builder = ExperimentBuilder()
        builder.add_sweep_definition(lambda simulation, value: {"p": value}, range(0, 2))
        experiment.builder = builder

        em = ExperimentManager(experiment=experiment, platform=test_platform)
        em.run()

        self.assertEqual(len(em.experiment.simulations), 2)
        self.assertEqual(em.experiment.assets.assets[0].filename, "working_model.py")
        self.assertEqual(em.experiment.simulations[0].tags, {'p': 0})
        self.assertEqual(em.experiment.simulations[1].tags, {'p': 1})

        test_platform.cleanup()

    @windows_only
    def test_build_emod_experiment_from_factory(self):
        test_platform = Platform('Test')
        experiment = model_factory.create("EMODExperiment", tags={"a": "1", "b": 2},
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

    def test_build_test_experiment_from_factory(self):
        test_experiment = TstExperiment()
        test_experiment.tags = {"a": "1", "b": 2}
        test_experiment.pre_creation()
        # Test create experiment with full model name
        experiment = model_factory.create(test_experiment.tags.get("type"), tags=test_experiment.tags)
        self.assertIsNotNone(experiment.uid)
        self.assertEqual(experiment.tags, {'a': '1', 'b': 2,
                                           'type': 'idmtools_test.utils.tst_experiment.TstExperiment'})

        # Test create experiment with sample model name
        experiment1 = model_factory.create("TstExperiment")
        self.assertIsNotNone(experiment1.uid)

        # Test create experiment with non-existing model name
        with self.assertRaises(ValueError) as context:
            model_factory.create("SomeExperiment")
        self.assertTrue("The ExperimentFactory could not create an experiment of type SomeExperiment" in
                        str(context.exception.args[0]))
