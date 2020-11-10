import os
import shutil
import unittest

from idmtools.services.ipersistance_service import IPersistenceService


class ITestWithPersistence(unittest.TestCase):
    current_directory = os.path.dirname(os.path.realpath(__file__))

    def setUp(self) -> None:
        self.data_dir = os.path.join(self.current_directory, "data")
        try:
            os.makedirs(self.data_dir, exist_ok=True)
        except FileExistsError:
            # Very Very Very rarely, high thread counts, we hit this error
            pass

        IPersistenceService.cache_directory = self.data_dir

    def tearDown(self) -> None:
        try:
            shutil.rmtree(self.data_dir)
        except Exception:
            pass
