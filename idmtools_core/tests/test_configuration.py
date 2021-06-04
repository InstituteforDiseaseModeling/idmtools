import allure
import tempfile
from shutil import copyfile
import io
import unittest.mock
import os
import pytest
from idmtools.config import IdmConfigParser
from idmtools.core import TRUTHY_VALUES
from idmtools.core.platform_factory import Platform
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.decorators import skip_if_global_configuration_is_enabled, run_in_temp_dir
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools_test.utils.utils import captured_output


@pytest.mark.smoke
@pytest.mark.serial
@allure.story("Configuration")
@allure.suite("idmtools_core")
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

    @skip_if_global_configuration_is_enabled
    def test_non_standard_name_fails_when_not_found(self):
        with self.assertRaises(FileNotFoundError) as err:
            IdmConfigParser(file_name="idmtools_does_not_exist.ini")
        self.assertIn("idmtools_does_not_exist.ini was not found!", err.exception.args[0])

    @skip_if_global_configuration_is_enabled
    @run_in_temp_dir
    def test_no_idmtools_common(self):
        with captured_output() as (out, err):
            IdmConfigParser(file_name="idmtools.ini")
            IdmConfigParser.ensure_init()
            max_workers = IdmConfigParser.get_option("COMMON", 'max_workers')
            self.assertIsNone(max_workers)
            self.assertIn("WARNING: File 'idmtools.ini' Not Found!", out.getvalue())

    # enable config only through special file
    @pytest.mark.skipif(not all([os.environ.get("TEST_GLOBAL_CONFIG", 'n').lower() in TRUTHY_VALUES, os.environ.get('IDMTOOLS_CONFIG_FILE', None) is None, not os.path.exists(IdmConfigParser.get_global_configuration_name())]), reason="Either the environment variable TEST_GLOBAL_CONFIG is not set to true, you already have a global configuration, or IDMTOOLS_CONFIG_FILE is set")
    def test_global_configuration(self):
        copyfile(os.path.join(os.path.dirname(__file__), "idmtools.ini"), IdmConfigParser.get_global_configuration_name())
        IdmConfigParser.ensure_init(dir_path=tempfile.gettempdir(), force=True)
        config_file = IdmConfigParser.get_config_path()
        self.assertEqual(config_file, IdmConfigParser.get_global_configuration_name())
        if os.path.exists(IdmConfigParser.get_global_configuration_name()):
            os.remove(IdmConfigParser.get_global_configuration_name())

    def test_has_idmtools_common(self):
        IdmConfigParser(file_name="idmtools.ini")
        IdmConfigParser.ensure_init(force=True)
        max_workers = IdmConfigParser.get_option("COMMON", 'max_workers')
        self.assertEqual(int(max_workers), 16)

    @pytest.mark.skipif(os.environ.get("IDMTOOLS_CONFIG_FILE", None) is not None, reason="You already have IDMTOOLS_CONFIG_FILE set")
    def test_environment_load(self):
        try:
            os.environ['IDMTOOLS_CONFIG_FILE'] = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "idmtools_cli", "tests", "idmtools.ini"))
            IdmConfigParser.ensure_init(force=True)
            self.assertEqual(IdmConfigParser.get_config_path(), os.environ['IDMTOOLS_CONFIG_FILE'])
        finally:
            del os.environ['IDMTOOLS_CONFIG_FILE']

    @pytest.mark.comps
    @unittest.mock.patch('idmtools_platform_comps.comps_platform.COMPSPlatform._login', side_effect=lambda: True)
    @pytest.mark.serial
    @skip_if_global_configuration_is_enabled
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

    def test_load_item_config_environment(self):
        os.environ['IDMTOOLS_TEST_ENV_CONFIG'] = "!"
        self.assertEqual(IdmConfigParser.get_option("test_env_config"), "!")

    @run_in_temp_dir
    def test_no_idmtools_values(self):
        IdmConfigParser(file_name="idmtools.ini")
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
