import unittest

from idmtools.registry.PlatformSpecification import PlatformPlugins


class TestCompsPlugin(unittest.TestCase):
    def test_comps_in_entrypoints(self):
        """
        This test requires the package is installed first. In then confirms that COMPS is detected by the
        PlatformPlugins manager
        Returns:

        """
        pl = PlatformPlugins()
        self.assertIn('COMPS', pl.get_plugin_map().keys())
