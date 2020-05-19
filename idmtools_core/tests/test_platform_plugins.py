from unittest import TestCase
from idmtools.registry.platform_specification import PlatformPlugins
from idmtools.utils.info import get_packages_from_pip


class TestPlatformPlugins(TestCase):
    def test_get_plugins(self):
        """
        Assumes we have plugins comps and local
        Returns:

        """
        pm = PlatformPlugins()
        self.assertGreater(len(pm.get_plugins()), 1)
        self.assertIn('COMPS', pm.get_plugin_map().keys())
        packages = get_packages_from_pip()

        if any(['idmtools-platform-comps' in p for p in packages]):
            from idmtools_platform_comps import COMPSPlatformSpecification
            COMPSSpec: COMPSPlatformSpecification = pm.get_plugin_map()['COMPS']
            examples = COMPSSpec.get_example_urls()
            self.assertGreater(len(examples), 1)
            self.assertIn('COMPS', pm.get_plugin_map().keys())
            self.assertIn('SSMT', pm.get_plugin_map().keys())
        if any(['idmtools-platform-local' in p for p in packages]):
            self.assertIn('Local', pm.get_plugin_map().keys())
        if any(['idmtools-platform-slurm' in p for p in packages]):
            self.assertIn('Slurm', pm.get_plugin_map().keys())
