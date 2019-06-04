import os
import unittest

from idmtools.platforms import COMPSPlatform
from idmtools.services.platforms import PlatformPersistService


class TestPlatformsServices(unittest.TestCase):

    def test_hashing(self):
        p = COMPSPlatform()
        PlatformPersistService.shelf_name = "ptests"
        PlatformPersistService.save(p)
        p2 = PlatformPersistService.retrieve(p.uid)
        self.assertDictEqual(p.__dict__, p2.__dict__)
        os.remove(os.path.join("..", "services", "ptests.db"))


if __name__ == '__main__':
    unittest.main()
