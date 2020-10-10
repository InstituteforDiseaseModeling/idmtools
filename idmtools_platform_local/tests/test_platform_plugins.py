from unittest import TestCase
from idmtools.registry.platform_specification import PlatformPlugins
import allure


@allure.story("LocalPlatform")
@allure.story("Plugins")
@allure.suite("idmtools_platform_local")
class TestPlatformPlugins(TestCase):
    def test_get_plugins(self):
        """
        Assumes we have plugins comps and local
        Returns:

        """
        pm = PlatformPlugins()
        self.assertGreater(len(pm.get_plugins()), 1)
        self.assertIn('Local', pm.get_plugin_map().keys())
