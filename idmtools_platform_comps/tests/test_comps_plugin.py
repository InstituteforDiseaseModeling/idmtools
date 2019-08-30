import unittest
import dataclasses
from idmtools.core import CacheEnabled
from idmtools.entities import IPlatform
from idmtools.registry.PlatformSpecification import PlatformPlugins
from idmtools_platform_comps.COMPSPlatform import COMPSPlatform
from idmtools_platform_comps.plugin_info import COMPSPlatformSpecification


class TestCompsPlugin(unittest.TestCase):
    def test_comps_in_entrypoints(self):
        """
        This test requires the package is installed first. In then confirms that COMPS is detected by the
        PlatformPlugins manager
        """
        pl = PlatformPlugins()
        self.assertIn('COMPS', pl.get_plugin_map().keys())

    def test_platform_short_name_is_comps(self):
        spec = COMPSPlatformSpecification()
        self.assertEqual("COMPS", spec.get_name())

    def test_example_config_contains_all_config_options(self):
        """
        Ensures all the example config contains all our possible config options

        """
        fields = dataclasses.fields(COMPSPlatform)
        exclude_fields = dataclasses.fields(IPlatform) + dataclasses.fields(CacheEnabled)

        spec = COMPSPlatformSpecification()
        example_config = spec.example_configuration()
        for field in fields:
            # skip private fields and not picklable as they are most lik
            if field.name[0] != '_' and field not in exclude_fields and not field.metadata.get('pickle_ignore', False):
                self.assertIn(field.name, example_config)
