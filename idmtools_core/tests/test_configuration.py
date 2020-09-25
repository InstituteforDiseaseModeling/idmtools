import io
import unittest.mock
import os
import pytest
from idmtools.config import IdmConfigParser
from idmtools.core.platform_factory import Platform
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence


@pytest.mark.smoke
@pytest.mark.serial
class TestConfig(ITestWithPersistence):

    def setUp(self):
        super().setUp()
        IdmConfigParser.clear_instance()

    def tearDown(self):
        super().tearDown()

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_section_found_case_independent(self, mock_stdout):
        insensitive = IdmConfigParser().get_section('CoMpS')
        sensitive = IdmConfigParser().get_section('COMPS')
        self.assertEqual(insensitive, sensitive)

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_section_not_found(self, mock_stdout):
        with self.assertRaises(ValueError) as context:
            IdmConfigParser().get_section('NotReallyASection')
        self.assertIn("Block 'NotReallyASection' doesn't exist!", context.exception.args[0])

    @pytest.mark.comps
    @unittest.mock.patch('idmtools_platform_comps.comps_platform.COMPSPlatform._login', side_effect=lambda: True)
    @pytest.mark.serial
    def test_simple_comps_platform_use_config(self, mock_login):
        platform = Platform("COMPS2")
        self.assertEqual(platform.endpoint, 'https://comps2.idmod.org')
        self.assertEqual(platform.environment, 'Bayesian')
        self.assertEqual(mock_login.call_count, 1)

    @pytest.mark.comps
    @unittest.mock.patch('idmtools_platform_comps.comps_platform.COMPSPlatform._login', side_effect=lambda: True)
    @pytest.mark.serial
    def test_simple_comps_platform_use_code(self, mock_login):
        platform = Platform("COMPS2", endpoint='https://abc', environment='Bayesian')
        self.assertEqual(platform.endpoint, 'https://abc')
        self.assertEqual(platform.environment, 'Bayesian')
        self.assertEqual(mock_login.call_count, 1)

    def test_idmtools_ini(self):
        config_file = IdmConfigParser.get_config_path()
        self.assertEqual(os.path.basename(config_file), 'idmtools.ini')

        max_threads = IdmConfigParser.get_option("COMMON", 'max_threads')
        self.assertEqual(int(max_threads), 16)

        idm = IdmConfigParser()
        max_threads = idm.get_option("COMMON", 'max_threads')
        self.assertEqual(int(max_threads), 16)

    def test_section(self):
        config_file = IdmConfigParser.get_config_path()
        self.assertEqual(os.path.basename(config_file), 'idmtools.ini')

        self.assertTrue(IdmConfigParser._config.has_section('COMPS'))

    def test_idmtools_ini_common_option(self):
        config_file = IdmConfigParser.get_config_path()
        self.assertEqual(os.path.basename(config_file), 'idmtools.ini')

        max_workers = IdmConfigParser.get_option("COMMON", 'max_workers')
        self.assertEqual(int(max_workers), 16)

        idm = IdmConfigParser()
        batch_size = idm.get_option("COMMON", 'batch_size')
        self.assertEqual(int(batch_size), 10)

    @pytest.mark.comps
    @unittest.mock.patch('idmtools_platform_comps.comps_platform.COMPSPlatform._login', side_effect=lambda: True)
    @pytest.mark.serial
    def test_idmtools_ini_option(self, login_mock):
        config_file = IdmConfigParser.get_config_path()
        self.assertEqual(os.path.basename(config_file), 'idmtools.ini')

        Platform('COMPS')
        max_workers = IdmConfigParser.get_option(None, 'max_workers')
        self.assertEqual(int(max_workers), 16)

        batch_size = IdmConfigParser.get_option(None, 'batch_size')
        self.assertEqual(int(batch_size), 10)

        not_exist = IdmConfigParser.get_option(None, 'batch_size_not_exist')
        print(not_exist)

    def test_no_idmtools_common(self):
        IdmConfigParser(file_name="idmtools_NotExist.ini")
        IdmConfigParser.ensure_init()
        max_workers = IdmConfigParser.get_option("COMMON", 'max_workers')
        self.assertIsNone(max_workers)
        # with self.assertRaises(Exception) as context:
        #     max_workers = IdmConfigParser.get_option("COMMON", 'max_workers')
        # self.assertIn('Config file NOT FOUND or IS Empty', context.exception.args[0])

        # self.assertIsNone(max_workers)

    def test_has_idmtools_common(self):
        IdmConfigParser(file_name="idmtools_NotExist.ini")
        IdmConfigParser.ensure_init(force=True)
        max_workers = IdmConfigParser.get_option("COMMON", 'max_workers')
        self.assertEqual(int(max_workers), 16)

    @pytest.mark.comps
    @unittest.mock.patch('idmtools_platform_comps.comps_platform.COMPSPlatform._login', side_effect=lambda: True)
    @pytest.mark.serial
    def test_idmtools_path(self, login_mock):
        IdmConfigParser(os.path.join(COMMON_INPUT_PATH, "configuration"), "idmtools_test.ini")
        platform = Platform('COMPS')
        self.assertEqual(platform.num_retries, int(IdmConfigParser.get_option('COMPS', 'num_retries')))

        file_path = os.path.join(COMMON_INPUT_PATH, "configuration", "idmtools_test.ini")
        self.assertEqual(IdmConfigParser.get_config_path(), os.path.abspath(file_path))

    def test_IdmConfigParser_singleton(self):
        p1 = IdmConfigParser()
        p2 = IdmConfigParser()

        self.assertEqual(p1, p2)
        self.assertEqual(id(p1), id(p2))

    def test_idmtools_ini_local(self):
        config_file = IdmConfigParser.get_config_path()
        self.assertEqual(os.path.basename(config_file), 'idmtools.ini')

        idm = IdmConfigParser()
        local_type = idm.get_option("Custom_Local", 'type')
        self.assertEqual(str(local_type), "Local")

    def test_no_idmtools(self):
        IdmConfigParser(file_name="idmtools_NotExist.ini")
        self.assertIsNone(IdmConfigParser.get_config_path())

        with self.assertRaises(ValueError) as context:
            IdmConfigParser(file_name="idmtools_NotExist.ini")
            IdmConfigParser.view_config_file()
        self.assertIn('Config file NOT FOUND or IS Empty!', context.exception.args[0])

    def test_no_idmtools_values(self):
        IdmConfigParser(file_name="idmtools_NotExist.ini")
        max_workers = IdmConfigParser.get_option(None, 'max_workers')
        batch_size = IdmConfigParser.get_option(None, 'batch_size')
        self.assertIsNone(max_workers)
        self.assertIsNone(batch_size)

    @pytest.mark.comps
    @unittest.mock.patch('idmtools_platform_comps.comps_platform.COMPSPlatform._login', side_effect=lambda: True)
    @pytest.mark.serial
    def test_idmtools_values(self, login_mock):
        Platform('COMPS')
        max_workers = IdmConfigParser.get_option(None, 'max_workers')
        batch_size = IdmConfigParser.get_option(None, 'batch_size')
        not_exist_option = IdmConfigParser.get_option(None, 'not_exist_option')
        self.assertEqual(int(max_workers), 16)
        self.assertEqual(int(batch_size), 10)
        self.assertIsNone(not_exist_option)

    @pytest.mark.comps
    @unittest.mock.patch('idmtools_platform_comps.comps_platform.COMPSPlatform._login', side_effect=lambda: True)
    def test_idmtools_no_section(self, login_mock):
        Platform('COMPS')
        max_workers = IdmConfigParser.get_option('NotExistSection', 'max_workers')
        batch_size = IdmConfigParser.get_option('NotExistSection', 'batch_size')
        self.assertIsNone(max_workers)
        self.assertIsNone(batch_size)
