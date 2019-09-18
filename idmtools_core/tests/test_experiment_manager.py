import os
import unittest
from idmtools.builders import ExperimentBuilder
from idmtools.core.platform_factory import Platform
from idmtools.managers import ExperimentManager
from idmtools.services.experiments import ExperimentPersistService
from idmtools.services.platforms import PlatformPersistService
from idmtools_models.python import PythonExperiment
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools_test.utils.tst_experiment import TstExperiment
from idmtools_test import COMMON_INPUT_PATH


def set_parameter_no_tags(simulation, value):
    simulation.set_parameter("p", value)


class TestExperimentManager(ITestWithPersistence):

    def test_from_experiment(self):
        e = TstExperiment("My experiment")
        p = Platform('Test')

        em = ExperimentManager(experiment=e, platform=p)
        em.run()

        em2 = ExperimentManager.from_experiment_id(e.uid, p)

        # Ensure we get the same thing when calling from_experiment
        self.assertEqual(em.experiment.base_simulation, em2.experiment.base_simulation)
        self.assertListEqual(em.experiment.children(), em2.experiment.children())

        # self.assertEqual(em.experiment, em2.experiment)  # not working for some reason; added more explicit tests
        self.assertEqual(em.experiment.uid, em2.experiment.uid)
        self.assertEqual(len(em.experiment.children()), len(em2.experiment.children()))
        self.assertEqual(sorted([s.uid for s in em.experiment.children()]), sorted([s.uid for s in em2.experiment.children()]))

        self.assertEqual(em.platform, em2.platform)
        self.assertEqual(em.platform.uid, em2.platform.uid)

    def test_from_experiment_unknown(self):
        c = Platform('Test')
        experiment = PythonExperiment(name="test_from_experiment",
                                      model_path=os.path.join(COMMON_INPUT_PATH, "compsplatform", "working_model.py"))
        builder = ExperimentBuilder()
        builder.add_sweep_definition(lambda simulation, value: {"p": value}, range(0, 2))
        experiment.builder = builder

        em = ExperimentManager(experiment=experiment, platform=c)
        em.run()
        self.assertEqual(len(em.experiment.children()), 2)

        # Delete the experiment and platform from the stores
        ExperimentPersistService.delete(em.experiment.uid)
        PlatformPersistService.delete(em.experiment.platform.uid)

        em2 = ExperimentManager.from_experiment_id(em.experiment.uid, platform=c)
        self.assertEqual(len(em2.experiment.children()), 2)
        self.assertIsInstance(em2.experiment, PythonExperiment)
        self.assertDictEqual(em2.experiment.tags, experiment.tags)
        self.assertEqual(em2.experiment.platform.uid, c.uid)

    def test_bad_experiment_builder(self):
        builder = ExperimentBuilder()
        with self.assertRaises(ValueError) as context:
            # test 'sim' (should be 'simulation') is bad parameter for add_sweep_definition()
            builder.add_sweep_definition(lambda sim, value: {"p": value}, range(0, 2))
        self.assertTrue('passed to SweepBuilder.add_sweep_definition needs to take a simulation argument!' in str(
            context.exception.args[0]))

    def test_bad_experiment_builder1(self):
        builder = ExperimentBuilder()
        with self.assertRaises(ValueError) as context:
            # test 'sim' is bad extra parameter for add_sweep_definition()
            builder.add_sweep_definition(lambda simulation, sim, value: {"p": value}, range(0, 2))
        self.assertTrue('passed to SweepBuilder.add_sweep_definition needs to only have simulation and exactly one free parameter.' in str(
            context.exception.args[0]))


if __name__ == '__main__':
    unittest.main()
