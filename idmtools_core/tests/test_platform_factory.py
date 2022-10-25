import allure
import os
import unittest.mock
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
        with self.assertRaises(ValueError) as context:
            Platform('NOTEXISTS')  # noqa:F841
        self.assertEqual("Block 'NOTEXISTS' doesn't exist!", str(context.exception.args[0]))

    @allure.story("Plugins")
    def test_bad_type(self):
        with self.assertRaises(ValueError) as context:
            Platform('BADTYPE')  # noqa:F841
        self.assertTrue("Bad is an unknown Platform Type. Supported platforms are" in str(context.exception.args[0]))

    @allure.story("Plugins")
    def test_no_type(self):
        with self.assertRaises(ValueError) as context:
            Platform('NOTYPE')
        self.assertIn('When creating a Platform you must specify the type in the block.', context.exception.args[0])

    @allure.story("Configuration")
    def test_block_is_none(self):
        with self.assertRaises(ValueError) as context:
            Platform(None)
        self.assertIn('Must have a valid Block name to create a Platform!', context.exception.args[0])

    @allure.story("Configuration")
    def test_no_block(self):
        try:
            Platform()
        except Exception as ex:
            self.assertIn("__new__() missing 1 required positional argument: 'block'", ex.args[0])

    @pytest.mark.comps
    @pytest.mark.timeout(60)
    @unittest.mock.patch('idmtools_platform_comps.comps_platform.COMPSPlatform._login', side_effect=lambda: True)
    @allure.story("COMPS")
    @allure.story("Configuration")
    def test_create_from_block(self, mock_login):
        p2 = Platform('COMPS')
        self.assertEqual(p2.__class__.__name__, 'COMPSPlatform')
        self.assertEqual(mock_login.call_count, 1)

        p3 = Platform('Test')
        self.assertEqual(p3.__class__.__name__, 'TestPlatform')
        p3.cleanup()
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

        platform3 = Platform('Test')
        self.assertEqual(platform3.__class__.__name__, 'TestPlatform')
        platform3.cleanup()

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
