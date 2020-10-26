import os
import unittest
import allure
import pytest
from idmtools.core.platform_factory import Platform
from idmtools_platform_comps.utils.package_version import get_docker_manifest, get_digest_from_docker_hub
from idmtools_platform_comps.utils.singularity_build import SingularityBuildWorkItem


@pytest.mark.comps
@allure.feature("Containsers")
class TestSingularityBuild(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        self.platform = Platform("COMPS2")

    def test_get_docker_manifest(self):
        manifest, tag = get_docker_manifest("idm/dtk-ubuntu-py3.7-mpich3.3-runtime:20.04.09")
        self.assertIsInstance(manifest, dict)
        self.assertEqual(manifest['config']['digest'], 'sha256:d0fd5396c017aa2b1da9022bb9e9ce420317b2bb36c3c3b4986da13b0c9755b9')

    @pytest.mark.skip
    def test_get_docker_manifest_latest(self):
        manifest, tag = get_docker_manifest("idm/dtk-ubuntu-py3.7-mpich3.3-runtime:latest")
        self.assertIsInstance(manifest, dict)
        self.assertEqual(manifest['config']['digest'], 'sha256:d0fd5396c017aa2b1da9022bb9e9ce420317b2bb36c3c3b4986da13b0c9755b9')
        self.assertEqual(tag, "idm/dtk-ubuntu-py3.7-mpich3.3-runtime:20.04.09")

    @pytest.mark.skip
    def test_get_dockerhub_latest(self):
        manifest = get_digest_from_docker_hub("alpine", "latest")
        self.assertIsInstance(manifest, str)
        self.assertEqual(manifest, 'sha256:d7342993700f8cd7aba8496c2d0e57be0666e80b4c441925fc6f9361fa81d10e')

    def test_get_dockerhub_version(self):
        manifest = get_digest_from_docker_hub("alpine", "3,12,1")
        self.assertIsInstance(manifest, str)
        self.assertEqual(manifest, 'sha256:d7342993700f8cd7aba8496c2d0e57be0666e80b4c441925fc6f9361fa81d10e')

    @pytest.mark.skip
    def test_get_ssmt_manifest_latest(self):
        manifest, tag = get_docker_manifest("idmtools/comps_ssmt_worker")
        self.assertEqual(tag, "'idmtools/comps_ssmt_worker:1.6.0.1'")
        self.assertIsInstance(manifest, dict)

    def test_docker_fetch_version_tag(self):
        sbi = SingularityBuildWorkItem()
        sbi.image_url = "docker://docker-production.packages.idmod.org/idm/dtk-ubuntu-py3.7-mpich3.3-runtime:20.04.09"
        getattr(sbi, '_SingularityBuildWorkItem__add_tags')()
        self.assertIn("docker_digest", sbi.image_tags)
        self.assertEqual(sbi.image_tags['docker_digest'], 'sha256:d0fd5396c017aa2b1da9022bb9e9ce420317b2bb36c3c3b4986da13b0c9755b9')
        self.assertEqual(sbi.image_tags['image_url'], 'docker://docker-production.packages.idmod.org/idm/dtk-ubuntu-py3.7-mpich3.3-runtime:20.04.09')

    def test_docker_fetch_version_from_dockerhub(self):
        sbi = SingularityBuildWorkItem()
        sbi.image_url = "docker://alpine:3.12.1"
        getattr(sbi, '_SingularityBuildWorkItem__add_tags')()
        self.assertIn("docker_digest", sbi.image_tags)
        self.assertEqual(sbi.image_tags['docker_digest'], 'sha256:d7342993700f8cd7aba8496c2d0e57be0666e80b4c441925fc6f9361fa81d10e')
        self.assertEqual(sbi.image_tags['image_url'], 'docker://alpine:3.12.1')
        js = sbi._prep_workorder_before_create()
        self.assertIsInstance(js, dict)
        self.assertIsInstance(sbi.work_order, dict)

    def test_comps_pull_alpine(self):
        sbi = SingularityBuildWorkItem()
        sbi.image_url = "docker://alpine:3.11.6"
        sbi.run(wait_until_done=True, platform=self.platform)

        self.assertTrue(sbi.succeeded)
