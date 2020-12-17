from unittest import mock

import allure
import tempfile
import os
import unittest
import dataclasses
import pytest
from idmtools import IdmConfigParser
from idmtools.core import CacheEnabled
from idmtools.core.platform_factory import Platform
from idmtools.entities.iplatform import IPlatform
from idmtools.entities.platform_requirements import PlatformRequirements
from idmtools.registry.platform_specification import PlatformPlugins
from idmtools_platform_comps.comps_platform import COMPSPlatform
from idmtools_platform_comps.plugin_info import COMPSPlatformSpecification
from idmtools_platform_comps.utils.package_version import IDMTOOLS_DOCKER_PROD, fetch_versions_from_server, get_latest_ssmt_image_version_from_artifactory


@allure.story("COMPS")
@allure.story("Plugins")
@allure.suite("idmtools_platform_comps")
class TestCompsPlugin(unittest.TestCase):
    @pytest.mark.smoke
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
            if field.name[0] != '_' and field not in exclude_fields and not field.metadata.get('pickle_ignore', False) \
                    and field.name != 'docker_image':
                self.assertIn(field.name, example_config)

    @pytest.mark.comps
    @pytest.mark.smoke
    def test_comps_requirements(self):
        with Platform("SLURM") as platform:
            self.assertTrue(platform.are_requirements_met(PlatformRequirements.LINUX))
            self.assertTrue(platform.are_requirements_met(PlatformRequirements.NativeBinary))
            self.assertTrue(platform.are_requirements_met(PlatformRequirements.PYTHON))
            self.assertFalse(platform.are_requirements_met(PlatformRequirements.WINDOWS))

    @pytest.mark.comps
    @pytest.mark.smoke
    def test_slurm_requirements(self):
        with Platform("COMPS2") as platform:
            self.assertFalse(platform.are_requirements_met(PlatformRequirements.LINUX))
            self.assertTrue(platform.are_requirements_met(PlatformRequirements.NativeBinary))
            self.assertTrue(platform.are_requirements_met(PlatformRequirements.PYTHON))
            self.assertTrue(platform.are_requirements_met(PlatformRequirements.WINDOWS))

    @pytest.mark.comps
    @pytest.mark.serial
    def test_platform_aliases(self):
        from idmtools.core.platform_factory import Platform
        org_directory = os.getcwd()
        try:
            with tempfile.TemporaryDirectory() as tmpdirname:
                print(f'Set working directory to {tmpdirname}')
                os.chdir(tmpdirname)
                IdmConfigParser.clear_instance()

                with Platform("BAYESIAN") as comps2:
                    self.assertEqual(comps2.endpoint, "https://comps2.idmod.org")
                    self.assertEqual(comps2.environment.upper(), "BAYESIAN")

                with Platform("SlurmStage") as comps2:
                    self.assertEqual(comps2.endpoint, "https://comps2.idmod.org")
                    self.assertEqual(comps2.environment.upper(), "SLURMSTAGE")
        except PermissionError as ex:
            print("Could not remove temp directory")
        except Exception as e:
            pass
        finally:
            print(f'Set working directory to {org_directory}')
            os.chdir(org_directory)
            IdmConfigParser.clear_instance()

    def test_get_ssmt_versions(self):
        url = os.path.join(IDMTOOLS_DOCKER_PROD, 'comps_ssmt_worker')
        versions = fetch_versions_from_server(url)
        prev_major = None
        pre_minor = None
        for ver in versions:
            parts = ver.split(".")
            if prev_major and prev_major and prev_major <= int(parts[0]) and pre_minor <= int(parts[1]):
                self.assertGreaterEqual(prev_major, int(parts[0]))
                self.assertGreaterEqual(pre_minor, int(parts[1]))
            prev_major = int(parts[0])
            pre_minor = int(parts[1])

    #
    def test_get_next_ssmt_version(self):
        test_versions = ['1.10.0.2', '1.10.0.1', '1.6.0.1', '1.5.1.7', '1.5.1.6', '1.5.0.2', '1.4.0.0', '1.3.0.0', '1.2.2.0', '1.2.0.0',
                         '1.1.0.2', '1.1.0.0', '1.0.1.0', '1.0.0', '1.0.0.0']
        with mock.patch('idmtools_platform_comps.utils.package_version.get_versions_from_site', return_value=test_versions) as mocK_fetch:
            self.assertEqual(get_latest_ssmt_image_version_from_artifactory(base_version="1.10.0.0"), "1.10.0.2")
            self.assertEqual(get_latest_ssmt_image_version_from_artifactory(base_version="1.5.0.1"), "1.5.1.7")
            self.assertEqual(get_latest_ssmt_image_version_from_artifactory(base_version="1.5.1.1"), "1.5.1.7")
            self.assertEqual(get_latest_ssmt_image_version_from_artifactory(base_version="1.5.1.7"), "1.5.1.7")
            self.assertEqual(get_latest_ssmt_image_version_from_artifactory(base_version="1.6.0.0"), "1.6.0.1")
            self.assertEqual(get_latest_ssmt_image_version_from_artifactory(base_version="1.1.0.0"), "1.1.0.2")
            self.assertEqual(get_latest_ssmt_image_version_from_artifactory(base_version="1.5.1+nightly.0"), "1.5.1.7")
            self.assertEqual(get_latest_ssmt_image_version_from_artifactory(base_version="1.6.0+nightly.0"), "1.6.0.1")
