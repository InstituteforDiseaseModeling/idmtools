from unittest.mock import patch

import allure
import os
import pytest
from dataclasses import fields
from idmtools.config import IdmConfigParser
from idmtools.core.platform_factory import Platform
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

    @allure.story("Configuration")
    def test_get_section(self):
        entries = IdmConfigParser.get_section('COMPS2')
        self.assertEqual(entries['endpoint'], 'https://comps2.idmod.org')

    def test_block_not_exits(self):
        with self.assertRaises(Exception) as context:
            Platform('NOTEXISTS')  # noqa:F841
        self.assertEqual("Type must be specified in Platform constructor.", str(context.exception.args[0]))

    @allure.story("Plugins")
    def test_bad_type(self):
        with self.assertRaises(ValueError) as context:
            Platform('BADTYPE')  # noqa:F841
        self.assertIn("Bad is an unknown Platform Type. Supported platforms are", str(context.exception.args[0]))

    @allure.story("Plugins")
    def test_no_type(self):
        with self.assertRaises(Exception) as context:
            Platform('NOTYPE')
        self.assertIn('None is an unknown Platform Type. Supported platforms are ',  context.exception.args[0])

    @allure.story("Configuration")
    def test_block_is_none(self):
        try:
            Platform(None)
        except Exception as ex:
            self.assertEqual("Type must be specified in Platform constructor.", ex.args[0])
    @allure.story("Configuration")
    def test_no_block(self):
        try:
            Platform()
        except Exception as ex:
            self.assertEqual("Type must be specified in Platform constructor.", ex.args[0])

    @allure.story("Configuration")
    def test_create_from_block(self):
        p = Platform('Test')
        self.assertEqual(p.__class__.__name__, 'TestPlatform')
        p.cleanup()

    def test_TestPlatform(self):
        platform = Platform('Test')
        members = platform.__dict__

        field_name = {f.name for f in fields(platform) if f.init}
        keys = field_name.intersection(members.keys())
        kwargs = {key: members[key] for key in keys if not key.startswith('_')}

        platform2 = Platform('Test', **kwargs)
        # same reason as above test
        platform.uid = None
        platform2.uid = None
        self.assertEqual(platform, platform2)
        platform2.cleanup()

    @patch("idmtools.config.idm_config_parser.user_logger")
    @patch('idmtools.core.platform_factory.logger')
    def test_create_platform_with_valid_block(self, mock_logger, mock_user_logger):
        block = 'My_container'
        platform = Platform(block)
        self.assertEqual(platform._config_block, block)
        self.assertEqual(platform.__class__.__name__, 'ContainerPlatform')
        self.assertEqual(platform._kwargs, {})
        self.assertIn('MY_JOB_DIRECTORY', platform.job_directory)
        # verify print correct block and job_directory
        mock_user_logger.log.call_args_list[0].assert_called_with('[My_container]')
        mock_user_logger.log.call_args_list[1].assert_called_with('"job_directory": "MY_JOB_DIRECTORY"')
        # verify type in block is not used
        mock_logger.warning.call_args_list[0].assert_called_with('the following Config Settings are not used when creating Platform:')
        mock_logger.warning.call_args_list[1].assert_called_with('- type = Container')

    @patch("idmtools.core.platform_factory.user_logger")
    @patch('idmtools.core.platform_factory.logger')
    def test_create_platform_with_valid_block_new_job_directory_from_platform(self, mock_logger, mock_user_logger):
        block = 'My_container'
        platform = Platform(block, job_directory="my_directory")
        self.assertEqual(platform._config_block, block)
        self.assertEqual(platform.__class__.__name__, 'ContainerPlatform')
        self.assertEqual(platform._kwargs, {'job_directory': 'my_directory'})
        # job_directory from block should be used
        self.assertIn('my_directory', platform.job_directory)
        mock_user_logger.log.call_args_list[0].assert_called_with('[My_container]')
        mock_user_logger.log.call_args_list[1].assert_called_with('"job_directory": "my_directory"')
        mock_logger.warning.call_args_list[0].assert_called_with('the following Config Settings are not used when creating Platform:')
        mock_logger.warning.call_args_list[1].assert_called_with('- type = Container')

    @patch("idmtools.core.platform_factory.user_logger")
    def test_create_platform_with_valid_block_other_kwargs(self, mock_user_logger):
        block = 'My_container'
        platform = Platform(block, docker_image="my_image")
        self.assertEqual(platform._config_block, block)
        self.assertEqual(platform.__class__.__name__, 'ContainerPlatform')
        self.assertEqual(platform._kwargs, {'docker_image': 'my_image'})
        # job_directory from block should be used
        self.assertIn('MY_JOB_DIRECTORY', platform.job_directory)
        mock_user_logger.log.call_args_list[0].assert_called_with('[My_container]')
        mock_user_logger.log.call_args_list[1].assert_called_with('"job_directory": "MY_JOB_DIRECTORY"')

    @patch("idmtools.core.platform_factory.user_logger")
    def test_create_platform_with_alias(self, mock_user_logger):
        kwargs = {'job_directory': 'destination_directory'}
        platform = Platform('Container', **kwargs)
        self.assertEqual(platform.__class__.__name__, 'ContainerPlatform')
        self.assertEqual(platform._config_block, 'Container')
        self.assertEqual(platform._kwargs, kwargs)
        self.assertIn('destination_directory', platform.job_directory)
        # verify print correct block and job_directory
        mock_user_logger.log.call_args_list[0].assert_called_with('[Container]')
        mock_user_logger.log.call_args_list[1].assert_called_with('"job_directory": "destination_directory"')

    def test_create_platform_with_random_block(self):
        kwargs = {'job_directory': 'destination_directory'}
        with self.assertRaises(ValueError) as context:
            platform = Platform("Container1", **kwargs)
        self.assertEqual('Type must be specified in Platform constructor.', str(context.exception))

    @patch('idmtools.core.platform_factory.user_logger')
    @patch('idmtools.core.platform_factory.logger')
    def test_create_platform_with_alias_and_non_used_type(self, mock_logger, mock_user_logger):
        kwargs = {'job_directory': 'destination_directory', 'type': 'Container1'}
        platform = Platform("Container", **kwargs)
        self.assertEqual(platform.__class__.__name__, 'ContainerPlatform')
        self.assertEqual(platform._config_block, 'Container')
        self.assertEqual(platform._kwargs, kwargs)
        self.assertIn('destination_directory', platform.job_directory)
        mock_logger.warning.call_args_list[0].assert_called_with("The following User Inputs are not used:")
        mock_logger.warning.call_args_list[1].assert_called_with("- type = Container1")
        mock_user_logger.log.call_args_list[0].assert_called_with('[Container]')
        mock_user_logger.log.call_args_list[1].assert_called_with('"job_directory": "destination_directory"')

    @patch('idmtools.core.platform_factory.user_logger')
    @patch('idmtools.core.platform_factory.logger')
    def test_create_platform_with_alias_and_valid_type(self, mock_logger, mock_user_logger):
        kwargs = {'job_directory': 'destination_directory', 'type': 'Container'}
        platform = Platform("Container", **kwargs)
        self.assertEqual(platform.__class__.__name__, 'ContainerPlatform')
        self.assertEqual(platform._config_block, 'Container')
        self.assertEqual(platform._kwargs, kwargs)
        self.assertIn('destination_directory', platform.job_directory)
        mock_user_logger.log.call_args_list[0].assert_called_with('[Container]')
        mock_user_logger.log.call_args_list[1].assert_called_with('"job_directory": "destination_directory"')
        mock_logger.warning.call_args_list[0].assert_called_with(
            'WARNING: The following User Inputs are not used:')
        mock_logger.warning.call_args_list[1].assert_called_with('- type = Container')

    @patch('idmtools.core.platform_factory.user_logger')
    @patch('idmtools.core.platform_factory.logger')
    def test_create_platform_with_no_block_and_valid_type(self, mock_logger, mock_user_logger):
        kwargs = {'job_directory': 'destination_directory', 'type': 'Container'}
        platform = Platform(**kwargs)
        self.assertEqual(platform.__class__.__name__, 'ContainerPlatform')
        self.assertEqual(platform._config_block, None)
        self.assertEqual(platform._kwargs, kwargs)
        self.assertIn('destination_directory', platform.job_directory)
        mock_logger.warning.call_args_list[0].assert_called_with(
            'WARNING: the following Config Settings are not used when creating Platform:')
        mock_logger.warning.call_args_list[1].assert_called_with('- type = Container')
    def test_create_platform_with_no_block_and_invalid_type(self):
        with self.assertRaises(Exception) as context:
            platform = Platform(type="Container1", job_directory="destination_directory")
        self.assertTrue(
            'Container1 is an unknown Platform Type. Supported platforms are ' in str(context.exception))

    @patch("idmtools.config.idm_config_parser.user_logger")
    @patch('idmtools.core.platform_factory.user_logger')
    @patch('idmtools.core.platform_factory.logger')
    def test_create_platform_with_ini_block_update_type_from_ini(self, mock_logger, mock_user_logger, mock_config_user_logger):
        block = 'My_container'
        kwargs = {'type': 'Container1'}
        platform = Platform(block, **kwargs)
        self.assertEqual(platform._config_block, block)
        self.assertEqual(platform.__class__.__name__, 'ContainerPlatform')
        self.assertEqual(platform._kwargs, kwargs)
        self.assertIn('MY_JOB_DIRECTORY', platform.job_directory)
        mock_logger.warning.call_args_list[0].assert_called_with("The following User Inputs are not used:")
        mock_logger.warning.call_args_list[1].assert_called_with("- type = Container1")
        mock_config_user_logger.log.call_args_list[0].assert_called_with('[My_container]')
        mock_config_user_logger.log.call_args_list[1].assert_called_with('"job_directory": "MY_JOB_DIRECTORY"')
        mock_user_logger.log.assert_not_called()

    @patch('idmtools.core.platform_factory.user_logger')
    @patch('idmtools.core.platform_factory.logger')
    def test_create_platform_with_non_exist_block_and_valid_type(self, mock_logger, mock_user_logger):
        kwargs = {'job_directory': 'destination_directory', 'type': 'Container'}
        platform = Platform('block', **kwargs)
        self.assertEqual(platform.__class__.__name__, 'ContainerPlatform')
        self.assertEqual(platform._config_block, 'block')
        self.assertEqual(platform._kwargs, kwargs)
        self.assertIn('destination_directory', platform.job_directory)
        mock_logger.warning.call_args_list[0].assert_called_with(
            "the following Config Settings are not used when creating Platform:")
        mock_logger.warning.call_args_list[1].assert_called_with("- block = block")
        mock_user_logger.log.call_args_list[0].assert_called_with('[block]')
        mock_user_logger.log.call_args_list[1].assert_called_with('"job_directory": "destination_directory"')

    @patch('idmtools.core.platform_factory.user_logger')
    @patch('idmtools.core.platform_factory.logger')
    def test_create_platform_with_non_exist_block_and_valid_type(self, mock_logger, mock_user_logger):
        kwargs = {'job_directory': 'destination_directory', 'any': 'something'}
        with self.assertRaises(Exception) as context:
            platform = Platform('block', **kwargs)
        self.assertTrue(
            "Type must be specified in Platform constructor." in str(context.exception.args[0]))
