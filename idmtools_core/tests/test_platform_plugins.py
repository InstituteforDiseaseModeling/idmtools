import os
import allure
import pytest
from idmtools import IdmConfigParser
from unittest import TestCase
from idmtools.registry.platform_specification import PlatformPlugins
from idmtools.utils.info import get_packages_from_pip

model_path = os.path.abspath(os.path.join("..", "..", "examples", "python_model", "inputs", "simple_python", "model.py"))
ID_PLUGIN_FAIL_MESSAGE = "Could not find the id plugin idmtools_id_generate_abcdefg defined by id_generator in your idmtools.ini. id_generator must be set to 'uuid' or 'item_sequence'"


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
