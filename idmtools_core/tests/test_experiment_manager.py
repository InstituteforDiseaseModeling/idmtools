import os
import shutil
import unittest

from idmtools.entities import IExperiment, ISimulation
from idmtools.managers import ExperimentManager
from idmtools.platforms import LocalPlatform
from idmtools.services.IPersistanceService import IPersistenceService
from idmtools.services.experiments import ExperimentPersistService
from idmtools.services.platforms import PlatformPersistService

current_directory = os.path.dirname(os.path.realpath(__file__))


class TestExperimentManager(unittest.TestCase):
    def setUp(self) -> None:
        self.data_dir = os.path.join(current_directory, "data")
        os.makedirs(self.data_dir, exist_ok=True)
        IPersistenceService.shelve_directory = self.data_dir
        PlatformPersistService.shelf_name = "ptests"
        ExperimentPersistService.shelf_name = "etests"

    def tearDown(self) -> None:
        shutil.rmtree(self.data_dir)

    def test_from_experiment(self):
        e = IExperiment("My experiment")
        p = LocalPlatform()

        e.uid = "123"
        e.platform_id = p.uid
        s = e.simulation()
        s.parameters = {"a": 1}

        s = e.simulation()
        s.parameters = {"a": 2}

        PlatformPersistService.save(p)
        ExperimentPersistService.save(e)

        em = ExperimentManager.from_experiment_id("123")

        self.assertEqual(em.experiment.simulations[0], e.simulations[0])
        self.assertEqual(em.experiment.simulations[1], e.simulations[1])
        self.assertEqual(em.experiment, e)
        self.assertEqual(em.platform, p)


if __name__ == '__main__':
    unittest.main()
