import os
from idmtools.config import IdmConfigParser
from idmtools.platforms import COMPSPlatform, LocalPlatform, PlatformType
from idmtools.platforms.PlatformFactory import PlatformFactory
from tests.utils.ITestWithPersistence import ITestWithPersistence


class TestConfig(ITestWithPersistence):

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_simple_comps_platform_use_config(self):
        platform = COMPSPlatform()
        self.assertEqual(platform.endpoint, 'https://comps2.idmod.org')
        self.assertEqual(platform.environment, 'Bayesian')

    def test_simple_comps_platform_use_code(self):
        platform = COMPSPlatform(endpoint='https://abc', environment='Bayesian')
        self.assertEqual(platform.endpoint, 'https://abc')
        self.assertEqual(platform.environment, 'Bayesian')

    def test_platform_factory(self):
        platform1 = PlatformFactory.get_platform(PlatformType.COMPSPlatform)
        self.assertTrue(isinstance(platform1, COMPSPlatform))

        platform2 = PlatformFactory.get_platform(PlatformType.LocalPlatform)
        self.assertTrue(isinstance(platform2, LocalPlatform))

        platform3 = PlatformFactory.get_platform("COMPSPlatform")
        self.assertTrue(isinstance(platform3, COMPSPlatform))

    def test_idmtools_ini(self):
        config_file = IdmConfigParser.get_config_path()
        self.assertEqual(os.path.basename(config_file), 'idmtools.ini')

        max_threads = IdmConfigParser.get_option("COMMON", 'max_threads')
        self.assertEqual(int(max_threads), 16)

