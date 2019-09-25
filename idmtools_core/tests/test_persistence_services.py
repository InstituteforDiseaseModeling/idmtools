import unittest
from idmtools.core.platform_factory import Platform
from idmtools.services.experiments import ExperimentPersistService
from idmtools.services.platforms import PlatformPersistService
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools_test.utils.tst_experiment import TstExperiment


class TestPersistenceServices(ITestWithPersistence):

    def test_persist_retrieve_platform(self):
        p = Platform('Test')
        PlatformPersistService.save(p)
        p2 = PlatformPersistService.retrieve(p.uid)
        self.assertEqual(p, p2)

    def test_persist_retrieve_experiment(self):
        e = TstExperiment("test")
        e.simulation()
        ExperimentPersistService.save(e)
        e2 = ExperimentPersistService.retrieve(e.uid)
        self.assertEqual(e, e2)
        # Simulations should not be persisted
        self.assertEqual(e2.simulations, [])

        e3 = ExperimentPersistService.retrieve("Missing")
        self.assertIsNone(e3)

    def test_pickle_experiment(self):
        import pickle

        e = TstExperiment("test")
        e.simulation()

        self.assertIsNotNone(e.base_simulation)

        ep = pickle.loads(pickle.dumps(e))

        self.assertIsNone(ep.base_simulation)


if __name__ == '__main__':
    unittest.main()
