import os
from idmtools.config import IdmConfigParser
from idmtools.platforms.PlatformFactory import PlatformFactory, PlatformType
from idmtools_platform_comps.COMPSPlatform import COMPSPlatform
from idmtools_platform_local.local_platform import LocalPlatform
from idmtools_test.utils.ITestWithPersistence import ITestWithPersistence


class TestConfig(ITestWithPersistence):

    def setUp(self):
        super().setUp()
        IdmConfigParser.clear_instance()

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

        idm = IdmConfigParser()
        max_threads = idm.get_option("COMMON", 'max_threads')
        self.assertEqual(int(max_threads), 16)

    def test_idmtools_path(self):
        IdmConfigParser("./inputs/configuration/", "idmtools_test.ini")
        platform = COMPSPlatform()
        self.assertEqual(platform.num_retires, int(IdmConfigParser.get_option('COMPSPLATFORM', 'num_retires')))

        file_path = os.path.join("./inputs/configuration/", "idmtools_test.ini")
        self.assertEqual(IdmConfigParser.get_config_path(), os.path.abspath(file_path))
