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

