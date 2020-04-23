from unittest import TestCase
from idmtools.registry.platform_specification import PlatformPlugins


class TestPlatformPlugins(TestCase):
    def test_get_plugins(self):
        """
        Assumes we have plugins comps and local
        Returns:

        """
        pm = PlatformPlugins()
        self.assertGreater(len(pm.get_plugins()), 1)
        self.assertIn('COMPS', pm.get_plugin_map().keys())
