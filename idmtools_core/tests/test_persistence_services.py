import os
import unittest

from idmtools.entities import IExperiment
from idmtools.platforms import LocalPlatform
from idmtools.services.experiments import ExperimentPersistService
from idmtools.services.platforms import PlatformPersistService
from tests.ITestWithPersistence import ITestWithPersistence
from tests.utilities.TestPlatform import TestPlatform

current_directory = os.path.dirname(os.path.realpath(__file__))


class TestPersistenceServices(ITestWithPersistence):

    def test_persist_retrieve_platform(self):
        p = LocalPlatform()
        PlatformPersistService.save(p)
        p2 = PlatformPersistService.retrieve(p.uid)
        self.assertEqual(p, p2)

        p = TestPlatform()
        PlatformPersistService.save(p)
        p2 = PlatformPersistService.retrieve(p.uid)
        self.assertEqual(p, p2)

    def test_persist_retrieve_experiment(self):
        e = IExperiment("test")
        e.simulation()
        e.simulation()
        ExperimentPersistService.save(e)
        e2 = ExperimentPersistService.retrieve(e.uid)
        self.assertEqual(e, e2)


if __name__ == '__main__':
    unittest.main()
