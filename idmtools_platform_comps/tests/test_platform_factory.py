import allure
import os
import unittest.mock
import pytest
from dataclasses import fields
from idmtools.config import IdmConfigParser
from idmtools.core.platform_factory import Platform
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence


@pytest.mark.smoke
@pytest.mark.serial
@allure.story("Core")
@allure.suite("idmtools_core")
class TestPlatformFactory(ITestWithPersistence):
    def setUp(self):
        super().setUp()
        IdmConfigParser.clear_instance()
        # Because of other tests, we cannot clear this properly. The best we can do is set it here so that tests that modify it don't effect this test
        os.environ['IDMTOOLS_ERROR_NO_CONFIG'] = "1"

    def tearDown(self):
        super().tearDown()

    def run_python_version(self, name):
        command = "python3 --version"
        task = CommandTask(command=command)
        experiment = Experiment.from_task(task, name=name)
        return experiment

    @pytest.mark.comps
    @pytest.mark.timeout(60)
    @unittest.mock.patch('idmtools_platform_comps.comps_platform.COMPSPlatform._login', side_effect=lambda: True)
    @allure.story("COMPS")
    @allure.story("Configuration")
    def test_create_from_block(self, mock_login):
        p2 = Platform('COMPS')
        self.assertEqual(p2.__class__.__name__, 'COMPSPlatform')
        self.assertEqual(mock_login.call_count, 1)
        del p2

    @pytest.mark.comps
    @pytest.mark.timeout(60)
    @unittest.mock.patch('idmtools_platform_comps.comps_platform.COMPSPlatform._login', side_effect=lambda: True)
    @allure.story("COMPS")
    @allure.story("Configuration")
    def test_platform_factory(self, mock_login):
        platform1 = Platform('COMPS')
        self.assertEqual(platform1.__class__.__name__, 'COMPSPlatform')
        self.assertEqual(mock_login.call_count, 1)

    @pytest.mark.comps
    @unittest.mock.patch('idmtools_platform_comps.comps_platform.COMPSPlatform._login', side_effect=lambda: True)
    @allure.story("COMPS")
    @allure.story("Configuration")
    def test_COMPSPlatform(self, mock_login):
        platform = Platform('COMPS')
        self.assertEqual(mock_login.call_count, 1)
        members = platform.__dict__

        field_name = {f.name for f in fields(platform) if f.init}
        keys = field_name.intersection(members.keys())
        kwargs = {key: members[key] for key in keys if not key.startswith('_')}

        platform2 = Platform('COMPS', **kwargs)
        self.assertEqual(mock_login.call_count, 2)
        # Note, due to new bug fix for platform uid(in iitem.py), we can not longer compare 2 platforms equal as before.
        # We used to have _uid member in platform which was comparison field and always None. Now, it has value with bug
        # fix. So in order to compare 2 platforms equal, let's ignore this property and compare rest of members
        platform.uid = None
        platform2.uid = None
        self.assertEqual(platform, platform2)

    @pytest.mark.comps
    @unittest.mock.patch('idmtools_platform_comps.comps_platform.COMPSPlatform._login', side_effect=lambda: True)
    def test_platform_factory_with_unkown_platform(self, mock_login):
        with self.assertRaises(ValueError) as context:
            platform = Platform('COMPS1', endpoint='https://comps.idmod.org', environment='Calculon')
        self.assertTrue(
            "Type must be specified in Platform constructor." in str(context.exception.args[0]))
    @pytest.mark.comps
    @unittest.mock.patch('idmtools_platform_comps.comps_platform.COMPSPlatform._login', side_effect=lambda: True)
    def test_platform_factory_with_ini(self, mock_login):
        platform = Platform('COMPS2')
        self.assertEqual(platform.__class__.__name__, 'COMPSPlatform')
        self.assertEqual(platform.endpoint, 'https://comps2.idmod.org')
        self.assertEqual(platform.environment, 'SlurmStage')

    @pytest.mark.comps
    @unittest.mock.patch('idmtools_platform_comps.comps_platform.COMPSPlatform._login', side_effect=lambda: True)
    def test_platform_factory_with_ini_and_update_required_fields(self, mock_login):
        # this case we first get all fields in COMPS2 block, then update endpoint and environment fields to new values
        # since type is just happen to the same, so we can create new platform object with these 3 new values
        platform = Platform('COMPS2', endpoint='https://comps.idmod.org', environment='Calculon')
        self.assertEqual(platform.endpoint, 'https://comps.idmod.org')
        self.assertEqual(platform.environment, 'Calculon')

    @pytest.mark.comps
    @unittest.mock.patch('idmtools.core.platform_factory.user_logger')
    @unittest.mock.patch('idmtools.core.platform_factory.logger')
    @unittest.mock.patch('idmtools_platform_comps.comps_platform.COMPSPlatform._login', side_effect=lambda: True)
    def test_platform_factory_with_ini_and_update_random_field(self, mock_login, mock_logger, mock_user_logger):
        platform = Platform('COMPS2', endpoint='https://comps.idmod.org', node='abcd')
        self.assertEqual(platform.__class__.__name__, 'COMPSPlatform')
        self.assertEqual(platform._config_block, 'COMPS2')
        mock_logger.warning.call_args_list[0].assert_called_with(
            f"call('\n/!\\ WARNING: The following User Inputs are not used:")
        mock_logger.warning.call_args_list[1].assert_called_with("- node = abcd")
        mock_user_logger.log.call_args_list[0].assert_called_with('\n[COMPS2]')
    @pytest.mark.comps
    @unittest.mock.patch('idmtools.core.platform_factory.user_logger')
    @unittest.mock.patch('idmtools.core.platform_factory.logger')
    @unittest.mock.patch('idmtools_platform_comps.comps_platform.COMPSPlatform._login', side_effect=lambda: True)
    def test_platform_factory_with_ini_and_update_valid_field(self, mock_login, mock_logger, mock_user_logger):
        platform = Platform('COMPS2', environment='Calculon')
        self.assertEqual(platform.__class__.__name__, 'COMPSPlatform')
        self.assertEqual(platform._config_block, 'COMPS2')
        mock_logger.warning.call_args_list[0].assert_called_with("The following User Inputs are not used:")
        mock_logger.warning.call_args_list[1].assert_called_with("- type = Container")
        mock_user_logger.log.call_args_list[0].assert_called_with('\n[COMPS2]')
        mock_user_logger.log.call_args_list[1].assert_called_with('"environment": "Calculon"')

    @pytest.mark.comps
    @unittest.mock.patch('idmtools.core.platform_factory.user_logger')
    @unittest.mock.patch('idmtools.core.platform_factory.logger')
    @unittest.mock.patch('idmtools_platform_comps.comps_platform.COMPSPlatform._login', side_effect=lambda: True)
    def test_platform_factory_with_ini_and_update_valid_field(self, mock_login, mock_logger, mock_user_logger):
        platform = Platform('COMPS2', environment='Calculon')
        self.assertEqual(platform.__class__.__name__, 'COMPSPlatform')
        self.assertEqual(platform._config_block, 'COMPS2')
        mock_user_logger.log.call_args_list[0].assert_called_with('\n[COMPS2]')
        mock_user_logger.log.call_args_list[1].assert_called_with('"environment": "Calculon"')
        mock_logger.warning.not_called()

    @pytest.mark.comps
    @unittest.mock.patch('idmtools_platform_comps.comps_platform.COMPSPlatform._login', side_effect=lambda: True)
    def test_platform_factory_with_random_block_and_valid_platform_fields(self, mock_login):
        kwargs = {'endpoint':'https://comps.idmod.org', 'environment': 'Calculon', 'type': 'COMPS'}
        platform = Platform('COMPS1', **kwargs)
        self.assertEqual(platform.__class__.__name__, 'COMPSPlatform')
        self.assertEqual(platform._config_block, 'COMPS1')
        self.assertEqual(platform._kwargs, kwargs)

    # After bug fix 2313
    @pytest.mark.comps
    @unittest.mock.patch('idmtools_platform_comps.comps_platform.COMPSPlatform._login', side_effect=lambda: True)
    def test_platform_factory_with_lowercase_type_value(self, mock_login):
        kwargs = {'endpoint':'https://comps.idmod.org', 'environment': 'Calculon', 'type': 'comps'}
        platform = Platform('COMPS1', **kwargs)
        self.assertEqual(platform.__class__.__name__, 'COMPSPlatform')
        self.assertEqual(platform._config_block, 'COMPS1')
        self.assertEqual(platform._kwargs, kwargs)

    @pytest.mark.comps
    @unittest.mock.patch('idmtools_platform_comps.comps_platform.COMPSPlatform._login', side_effect=lambda: True)
    def test_platform_factory_with_no_exist_block_no_type(self, mock_login):
        kwargs = {'endpoint':'https://comps2.idmod.org', 'environment': 'SlurmStage'}
        with self.assertRaises(ValueError) as context:
            platform = Platform("my_block", **kwargs)
            self.assertIn("my_block is an unknown Platform Type. Supported platforms are", str(context.exception.args[0]))

    @pytest.mark.comps
    @pytest.mark.timeout(60)
    def test_with_experiment_with_alias(self):
        platform = Platform('SlurmStage')
        exp = self.run_python_version("test_with_alias")
        exp.run(wait_until_done=True, platform=platform)
        self.assertTrue(exp.succeeded)

    @pytest.mark.comps
    @pytest.mark.timeout(60)
    def test_with_experiment_with_ini(self):
        platform = Platform('COMPS2')
        exp = self.run_python_version("test_with_ini")
        exp.run(wait_until_done=True, platform=platform)
        self.assertTrue(exp.succeeded)

    @pytest.mark.comps
    @pytest.mark.timeout(60)
    def test_with_experiment_with_no_block(self):
        platform = Platform(endpoint='https://comps2.idmod.org', environment='SlurmStage', type='COMPS')
        exp = self.run_python_version("test_with_no_block")
        exp.run(wait_until_done=True, platform=platform)
        self.assertTrue(exp.succeeded)

    @pytest.mark.comps
    @pytest.mark.timeout(60)
    def test_with_experiment_with_block_and_valid_fields(self):
        platform = Platform("my_block", endpoint='https://comps2.idmod.org', environment='SlurmStage', type='COMPS')
        exp = self.run_python_version("test_with_block_and_valid_fields")
        exp.run(wait_until_done=True, platform=platform)
        self.assertTrue(exp.succeeded)

    @pytest.mark.comps
    @pytest.mark.timeout(60)
    def test_with_experiment_with_ini_and_update(self):
        platform = Platform('COMPS2', node_group="idm_abcd")
        exp = self.run_python_version("test_with_ini_and_update")
        exp.run(wait_until_done=True, platform=platform)
        self.assertTrue(exp.succeeded)

    @pytest.mark.comps
    @pytest.mark.timeout(60)
    def test_with_experiment_with_ini_and_invalid_update(self):
        with self.assertRaises(RuntimeError) as context:
            platform = Platform('COMPS2', environment="Calculon")
            exp = self.run_python_version("test_with_ini_and_invalid_update")
            exp.run(platform=platform)
        print(str(context.exception.args[0]))
        self.assertTrue("invalid environment-name: Calculon" in str(context.exception.args[0]))

    @pytest.mark.comps
    @pytest.mark.timeout(60)
    def test_with_experiment_with_no_type_no_block(self):
        with self.assertRaises(Exception) as context:
            platform = Platform(endpoint='https://comps2.idmod.org', environment='SlurmStage')
            exp = self.run_python_version("test_with_no_type_no_block")
            exp.run(platform=platform)
        self.assertEqual("Type must be specified in Platform constructor.", str(context.exception.args[0]))

    @pytest.mark.comps
    @pytest.mark.timeout(60)
    def test_with_experiment_with_no_alias_block(self):
        with self.assertRaises(ValueError) as context:
            platform = Platform(block="My_Stage")
            exp = self.run_python_version("test_no_alias_block")
            exp.run(platform=platform)
        self.assertTrue("Type must be specified in Platform constructor." in str(context.exception.args[0]))

