import dataclasses

import allure
import unittest
from idmtools.entities.iplatform import IPlatform
from idmtools.registry.platform_specification import PlatformPlugins
from idmtools_platform_local.local_platform import LocalPlatform
from idmtools_platform_local.plugin_info import LocalPlatformSpecification


@allure.story("LocalPlatform")
@allure.story("Plugins")
@allure.suite("idmtools_platform_local")
class TestLocalPlatformPlugin(unittest.TestCase):
    def test_local_in_entrypoints(self):
        """
        This test requires the package is installed first. In then confirms that Local is detected by the
        PlatformPlugins manager
        """
        pl = PlatformPlugins()
        self.assertIn('Local', pl.get_plugin_map().keys())

    def test_platform_short_name_is_local(self):
        spec = LocalPlatformSpecification()
        self.assertEqual("Local", spec.get_name())

    def test_example_config_contains_all_config_options(self):
        """
        Ensures all the example config contains all our possible config fields

        """
        fields = dataclasses.fields(LocalPlatform)
        exclude_fields = dataclasses.fields(IPlatform)
        spec = LocalPlatformSpecification()
        example_config = spec.example_configuration()
        for field in fields:
            # skip private fields
            if field.name[0] != '_' and field not in exclude_fields and not field.metadata.get('pickle_ignore', False):
                self.assertIn(field.name, example_config)
