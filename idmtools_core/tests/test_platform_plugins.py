import allure
import pytest
from idmtools import IdmConfigParser
from unittest import TestCase
from idmtools.registry.platform_specification import PlatformPlugins


@pytest.mark.smoke
@allure.story("Plugins")
@allure.suite("idmtools_core")
class TestPlatformPlugins(TestCase):
    def tearDown(self) -> None:
        IdmConfigParser.clear_instance()
        super().tearDown()

    def test_get_plugins(self):
        """
        Assumes we have plugins comps and local
        Returns:
        """
        pm = PlatformPlugins()
        self.assertGreater(len(pm.get_plugins()), 1)
        self.assertIn('Test', pm.get_plugin_map().keys())
        self.assertIn('TestExecute', pm.get_plugin_map().keys())

