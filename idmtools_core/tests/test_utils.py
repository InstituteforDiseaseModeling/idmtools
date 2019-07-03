import unittest

from idmtools.core import ExperimentNotFound
from idmtools.services.experiments import ExperimentPersistService
from idmtools.utils.entities import retrieve_experiment
from tests.utils.ITestWithPersistence import ITestWithPersistence
from tests.utils.TestExperiment import TestExperiment
from tests.utils.TestPlatform import TestPlatform


class TestUtils(ITestWithPersistence):

    def test_retrieve_experiment(self):
        # Test missing
        with self.assertRaises(ExperimentNotFound):
            retrieve_experiment("Missing", TestPlatform())

        # Test correct retrieval
        e = TestExperiment("test")
        ExperimentPersistService.save(e)

        e2 = retrieve_experiment(e.uid)
        self.assertEqual(e, e2)

        # test correct retrieval with platform
        e = TestExperiment("test2")
        p = TestPlatform()
        p.create_experiment(e)
        e.platform_id = p.uid
        with self.assertRaises(ExperimentNotFound):
            e2 = retrieve_experiment(e.uid)
        e2 = retrieve_experiment(e.uid, p)
        self.assertEqual(e2, e)


if __name__ == '__main__':
    unittest.main()
