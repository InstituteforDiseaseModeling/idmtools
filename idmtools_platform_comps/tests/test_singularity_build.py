import os
import unittest
import allure
import pytest
from idmtools.assets import Asset
from idmtools.core.platform_factory import Platform
from idmtools_platform_comps.utils.package_version import get_docker_manifest, get_digest_from_docker_hub
from idmtools_platform_comps.utils.singularity_build import SingularityBuildWorkItem
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.decorators import linux_only
from idmtools_test.utils.utils import get_case_name


@pytest.mark.comps
@allure.feature("Containers")
class TestSingularityBuild(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.case_name = get_case_name(os.path.basename(__file__) + "--" + self._testMethodName)
        self.platform = Platform("SlurmStage")

    def test_get_docker_manifest(self):
        manifest, tag = get_docker_manifest("idm/dtk-ubuntu-py3.7-mpich3.3-runtime:20.04.09")
        self.assertIsInstance(manifest, dict)
        self.assertEqual(manifest['config']['digest'], 'sha256:d0fd5396c017aa2b1da9022bb9e9ce420317b2bb36c3c3b4986da13b0c9755b9')

    # we can't do this everytime since latest changes
    @pytest.mark.skip
    def test_get_docker_manifest_latest(self):
        manifest, tag = get_docker_manifest("idm/dtk-ubuntu-py3.7-mpich3.3-runtime:latest")
        self.assertIsInstance(manifest, dict)
        self.assertEqual(manifest['config']['digest'], 'sha256:d0fd5396c017aa2b1da9022bb9e9ce420317b2bb36c3c3b4986da13b0c9755b9')
        self.assertEqual(tag, "idm/dtk-ubuntu-py3.7-mpich3.3-runtime:20.04.09")

    # we can't do this everytime since latest changes
    @pytest.mark.skip
    def test_get_dockerhub_latest(self):
        manifest = get_digest_from_docker_hub("alpine", "latest")
        self.assertIsInstance(manifest, str)
        self.assertEqual(manifest, 'sha256:d7342993700f8cd7aba8496c2d0e57be0666e80b4c441925fc6f9361fa81d10e')

    def test_get_dockerhub_version(self):
        manifest = get_digest_from_docker_hub("alpine", "3.12.1")
        self.assertIsInstance(manifest, str)
        self.assertEqual(manifest, 'sha256:d7342993700f8cd7aba8496c2d0e57be0666e80b4c441925fc6f9361fa81d10e')

    @pytest.mark.skip
    def test_get_ssmt_manifest_latest(self):
        manifest, tag = get_docker_manifest("idmtools/comps_ssmt_worker")
        self.assertEqual(tag, "idmtools/comps_ssmt_worker:1.6.0.1")
        self.assertIsInstance(manifest, dict)

    def test_docker_fetch_version_tag(self):
        sbi = SingularityBuildWorkItem(name=self.case_name)
        sbi.image_url = "docker://docker-production.packages.idmod.org/idm/dtk-ubuntu-py3.7-mpich3.3-runtime:20.04.09"
        getattr(sbi, '_SingularityBuildWorkItem__add_tags')()
        self.assertIn("digest", sbi.image_tags)
        self.assertEqual(sbi.image_tags['digest'], 'sha256:d0fd5396c017aa2b1da9022bb9e9ce420317b2bb36c3c3b4986da13b0c9755b9')
        self.assertEqual(sbi.image_tags['image_url'], 'docker://docker-production.packages.idmod.org/idm/dtk-ubuntu-py3.7-mpich3.3-runtime:20.04.09')

    def test_docker_fetch_version_from_dockerhub(self):
        sbi = SingularityBuildWorkItem(name=self.case_name)
        sbi.image_url = "docker://alpine:3.12.1"
        getattr(sbi, '_SingularityBuildWorkItem__add_tags')()
        self.assertIn("digest", sbi.image_tags)
        self.assertEqual(sbi.image_tags['digest'], 'sha256:d7342993700f8cd7aba8496c2d0e57be0666e80b4c441925fc6f9361fa81d10e')
        self.assertEqual(sbi.image_tags['image_url'], 'docker://alpine:3.12.1')
        js = sbi._prep_work_order_before_create()
        self.assertIsInstance(js, dict)
        self.assertIsInstance(sbi.work_order, dict)

    def test_comps_pull_alpine(self):
        # How can we make this test repeatable other than force?
        sbi = SingularityBuildWorkItem()
        sbi.image_url = "docker://alpine:3.11.6"
        sbi.run(wait_until_done=True, platform=self.platform)
        self.assertTrue(sbi.succeeded)
        self.assertIsNotNone(sbi.asset_collection)

    # because of new lines on python files, we have to make this different on different platforms
    @linux_only
    def test_singularity_context_basic(self):
        sbi = self.get_alpine_simple_builder()
        self.assertEqual(sbi.context_checksum(), "sha256:1066d04968886be732aa5155c45458dbf42141de4175c721cf99fcff71c0ff4a")
        # test it changes with a new file
        sbi.add_asset(Asset(filename="example.py", content="Blah blah blah"))
        self.assertEqual(sbi.context_checksum(), "sha256:a13eb1930c8727ecaa6549a3f2a19ea34db99d082d6a7c29c0ac9a6efd7bd606")

    def get_alpine_simple_builder(self):
        sing_dir = os.path.join(COMMON_INPUT_PATH, 'singularity', 'alpine_simple')
        def_file = os.path.join(sing_dir, 'Singularity.def')
        sbi = SingularityBuildWorkItem(definition_file=def_file)
        sbi.add_asset(os.path.join(sing_dir, "run_model.py"))
        return sbi

    def test_singularity_from_definition(self):
        sbi = self.get_alpine_simple_builder()
        sbi.run(wait_until_done=True)
        self.assertTrue(sbi.succeeded)
        self.assertIsNotNone(sbi.asset_collection)

    def test_singularity_template(self):
        sing_dir = os.path.join(COMMON_INPUT_PATH, 'singularity', 'alpine_template')
        def_file = os.path.join(sing_dir, 'Singularity.jinja')
        sbi = SingularityBuildWorkItem(
            name=self.case_name,
            definition_file=def_file, is_template=True,
            template_args=dict(python_version='3.8.6', packages=['numpy', 'pandas', 'requests'])
        )
        rendered_def = sbi.render_template()
        self.assertEqual(rendered_def, """Bootstrap: docker
From: python:3.8.6

%post
    apt-get -y update && apt-get install -y gcc
    pip3 install wheel
    pip3 install numpy pandas requests 

%runscript
    echo "Container was created $NOW"
    echo "Arguments received: $*"
    exec "$@"

%environment
    export MPLBACKEND=Agg

%labels
    Author ccollins@idmod.org
    Version v0.0.1

%help
    This is a demo container used to demo idmtools templates""")
        sbi.run(wait_until_done=True, platform=self.platform)
        self.assertTrue(sbi.succeeded)
        self.assertIsNotNone(sbi.asset_collection)




