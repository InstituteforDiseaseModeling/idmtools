import os
import shutil
import unittest

from idmtools.entities import IExperiment
from idmtools.platforms import LocalPlatform
from idmtools.services.IPersistanceService import IPersistenceService
from idmtools.services.experiments import ExperimentPersistService
from idmtools.services.platforms import PlatformPersistService

current_directory = os.path.dirname(os.path.realpath(__file__))


class TestPersistenceServices(unittest.TestCase):
    def setUp(self) -> None:
        self.data_dir = os.path.join(current_directory, "data")
        os.makedirs(self.data_dir, exist_ok=True)
        IPersistenceService.shelve_directory = self.data_dir
        PlatformPersistService.shelf_name = "ptests"
        ExperimentPersistService.shelf_name = "etests"

    def tearDown(self) -> None:
        shutil.rmtree(self.data_dir)

    def test_persist_retrieve_platform(self):
        p = LocalPlatform()
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
