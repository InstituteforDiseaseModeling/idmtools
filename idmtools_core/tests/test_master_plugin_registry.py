from unittest import TestCase
import allure
import pytest
from idmtools.registry.master_plugin_registry import MasterPluginRegistry
from idmtools.utils.info import get_packages_from_pip


@pytest.mark.smoke
@allure.story("Plugins")
@allure.suite("idmtools_core")
@pytest.mark.skip("failed in github")
class TestMasterPluginRegistry(TestCase):
    def test_get_plugins(self):
        """
        Assumes we have plugins comps and local
        Returns:

        """
        packages = get_packages_from_pip()
        pm = MasterPluginRegistry()
        self.assertGreater(len(pm.get_plugins()), 1)
        if any(['idmtools-platform-comps' in p for p in packages]):
            self.assertIn('COMPSPlatform', pm.get_plugin_map().keys())
            self.assertIn('SSMTPlatform', pm.get_plugin_map().keys())
        if any(['idmtools-platform-local' in p for p in packages]):
            self.assertIn('LocalPlatform', pm.get_plugin_map().keys())
        if any(['idmtools-platform-slurm' in p for p in packages]):
            self.assertIn('SlurmPlatform', pm.get_plugin_map().keys())
        if any(['idmtools-models' in p for p in packages]):
            for task in ['Python', 'R', 'JSONConfigured', 'JSONConfiguredPython', 'R', 'Docker']:
                self.assertIn(f'{task}Task', pm.get_plugin_map().keys())
