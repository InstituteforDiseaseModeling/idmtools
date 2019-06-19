import unittest

from idmtools.managers import ExperimentManager
from tests.utils.ITestWithPersistence import ITestWithPersistence
from tests.utils.TestExperiment import TestExperiment
from tests.utils.TestPlatform import TestPlatform


def set_parameter_no_tags(simulation, value):
    simulation.set_parameter("p", value)


class TestExperimentManager(ITestWithPersistence):

    def test_from_experiment(self):
        e = TestExperiment("My experiment")
        p = TestPlatform()

        em = ExperimentManager(experiment=e, platform=p)
        em.run()

        em2 = ExperimentManager.from_experiment_id(e.uid)

        # Ensure we get the same thing when calling from_experiment
        self.assertEqual(em.experiment.base_simulation, em2.experiment.base_simulation)
        self.assertListEqual(em.experiment.simulations, em2.experiment.simulations)
        self.assertEqual(em.experiment, em2.experiment)
        self.assertEqual(em.platform, em2.platform)


if __name__ == '__main__':
    unittest.main()
