import allure
import pickle
import unittest

import pytest
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools.services.platforms import PlatformPersistService
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools_test.utils.test_task import TestTask
from idmtools.config import IdmConfigParser


@pytest.mark.smoke
@pytest.mark.serial
@allure.story("Core")
@allure.story("Cache")
@allure.suite("idmtools_core")
class TestPersistenceServices(ITestWithPersistence):
    def setUp(self):
        super().setUp()
        IdmConfigParser.clear_instance()

    def tearDown(self):
        super().tearDown()

    def test_persist_retrieve_platform(self):
        p = Platform('Test')
        PlatformPersistService.save(p)
        p2 = PlatformPersistService.retrieve(p.uid)
        self.assertEqual(p, p2)
        p.cleanup()

    def test_pickle_experiment(self):
        e = Experiment("test")
        e.simulations.append(Simulation(task=TestTask()))

        self.assertIsNotNone(e.simulations)
        self.assertEqual(len(e.simulations), 1)

        ep = pickle.loads(pickle.dumps(e))

        self.assertEqual(ep.simulations[0], e.simulations[0])

    def test_platform_cache_clear(self):
        p1 = Platform('Test')
        PlatformPersistService.save(p1)
        self.assertTrue(PlatformPersistService.length())
        PlatformPersistService.clear()
        self.assertEqual(PlatformPersistService.length(), 0)


if __name__ == '__main__':
    unittest.main()
