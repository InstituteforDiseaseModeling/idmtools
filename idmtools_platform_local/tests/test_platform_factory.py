import allure
import pytest
from dataclasses import fields
from idmtools.config import IdmConfigParser
from idmtools.core.platform_factory import Platform
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools_test.utils.confg_local_runner_test import get_test_local_env_overrides


@allure.story("LocalPlatform")
@allure.story("Plugins")
@allure.suite("idmtools_platform_local")
class TestPlatformFactory(ITestWithPersistence):
    def setUp(self):
        super().setUp()
        IdmConfigParser.clear_instance()

    def tearDown(self):
        super().tearDown()

    @pytest.mark.docker
    @pytest.mark.serial
    def test_platform_factory(self):
        custom_local_platform = Platform('Custom_Local', **get_test_local_env_overrides())
        self.assertEqual(custom_local_platform.__class__.__name__, 'LocalPlatform')
        del custom_local_platform

        local_platform = Platform('Local', **get_test_local_env_overrides())
        self.assertEqual(local_platform.__class__.__name__, 'LocalPlatform')
        del local_platform

    @pytest.mark.docker
    @pytest.mark.timeout(60)
    @pytest.mark.serial
    def test_LocalPlatform(self):
        platform = Platform('Custom_Local', **get_test_local_env_overrides())
        members = platform.__dict__

        field_name = {f.name for f in fields(platform) if f.init}
        keys = field_name.intersection(members.keys())
        kwargs = {key: members[key] for key in keys if not key.startswith('_')}

        platform2 = Platform('Local', **kwargs)
        # override this to make only part unique the same
        platform2._config_block = platform._config_block
        platform.uid = None
        platform2.uid = None
        self.assertEqual(platform, platform2)
        del platform
        del platform2
