import os
import shutil
import unittest
import allure
import pytest
from idmtools.assets import Asset
from idmtools.core import TRUTHY_VALUES
from idmtools.core.platform_factory import Platform
from idmtools_platform_comps.utils.package_version import get_docker_manifest, get_digest_from_docker_hub
from idmtools_platform_comps.utils.singularity_build import SingularityBuildWorkItem
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.decorators import linux_only, windows_only
from idmtools_test.utils.utils import get_case_name

# Force test cases subject to caching to re-run
# Set to 1 or t, or on to force
FORCE = os.getenv("FORCE_SBI_TESTS", '0') in TRUTHY_VALUES


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
        self.assertEqual(manifest, 'sha256:cb64bbe7fa613666c234e1090e91427314ee18ec6420e9426cf4e7f314056813')

    @windows_only
    def test_get_dockerhub_version(self):
        manifest = get_digest_from_docker_hub("alpine", "3.12.1")
        self.assertIsInstance(manifest, str)
        self.assertEqual(manifest, 'sha256:cb64bbe7fa613666c234e1090e91427314ee18ec6420e9426cf4e7f314056813')

    @pytest.mark.skip
    def test_get_ssmt_manifest_latest(self):
        manifest, tag = get_docker_manifest("idmtools/comps_ssmt_worker")
        self.assertEqual(tag, "idmtools/comps_ssmt_worker:1.6.0.1")
        self.assertIsInstance(manifest, dict)

    def test_docker_fetch_version_tag(self):
        sbi = SingularityBuildWorkItem(name=self.case_name, force=FORCE)
        sbi.image_url = "docker://docker-production.packages.idmod.org/idm/dtk-ubuntu-py3.7-mpich3.3-runtime:20.04.09"
        getattr(sbi, '_SingularityBuildWorkItem__add_tags')()
        self.assertIn('image_name', sbi.image_tags)
        self.assertEqual(sbi.image_tags['image_name'], 'idm_dtk-ubuntu-py3.7-mpich3.3-runtime_20.04.09.sif')
        self.assertIn("digest", sbi.image_tags)
        self.assertEqual(sbi.image_tags['digest'], 'sha256:d0fd5396c017aa2b1da9022bb9e9ce420317b2bb36c3c3b4986da13b0c9755b9')
        self.assertEqual(sbi.image_tags['image_url'], 'docker://docker-production.packages.idmod.org/idm/dtk-ubuntu-py3.7-mpich3.3-runtime:20.04.09')

    @windows_only
    def test_docker_fetch_version_from_dockerhub(self):
        sbi = SingularityBuildWorkItem(name=self.case_name, force=FORCE)
        sbi.image_url = "docker://alpine:3.12.1"
        getattr(sbi, '_SingularityBuildWorkItem__add_tags')()
        self.assertIn("digest", sbi.image_tags)
        self.assertIn('image_name', sbi.image_tags)
        self.assertEqual(sbi.image_tags['image_name'], 'alpine_3.12.1.sif')
        self.assertEqual(sbi.image_tags['digest'], 'sha256:cb64bbe7fa613666c234e1090e91427314ee18ec6420e9426cf4e7f314056813')
        self.assertEqual(sbi.image_tags['image_url'], 'docker://alpine:3.12.1')
        js = sbi._prep_work_order_before_create()
        self.assertIsInstance(js, dict)
        self.assertIsInstance(sbi.work_order, dict)

    def test_comps_pull_alpine(self):
        # How can we make this test repeatable other than force?
        sbi = SingularityBuildWorkItem(force=FORCE)
        sbi.image_url = "docker://alpine:3.11.6"
        sbi.run(wait_until_done=True, platform=self.platform)
        self.assertTrue(sbi.succeeded)
        self.assertIsNotNone(sbi.asset_collection)
        self.assertIn('image_name', sbi.image_tags)
        self.assertIn('created_by', sbi.image_tags)
        asset_file = os.path.join(os.curdir, "alpine_3.11.6.sif.asset_id")
        self.assertTrue(os.path.exists(asset_file))
        os.remove(asset_file)

    # because of new lines on python files, we have to make this different on different platforms
    # we can't do this everytime since latest changes
    @linux_only
    @pytest.mark.skip
    def test_singularity_context_basic(self):
        sbi = self.get_alpine_simple_builder()
        self.assertEqual(sbi.context_checksum(), "sha256:1066d04968886be732aa5155c45458dbf42141de4175c721cf99fcff71c0ff4a")
        # test it changes with a new file
        sbi.add_asset(Asset(filename="example.py", content="Blah blah blah"))
        self.assertEqual(sbi.context_checksum(), "sha256:a13eb1930c8727ecaa6549a3f2a19ea34db99d082d6a7c29c0ac9a6efd7bd606")

    def get_alpine_simple_builder(self):
        sing_dir = os.path.join(COMMON_INPUT_PATH, 'singularity', 'alpine_simple')
        def_file = os.path.join(sing_dir, 'Singularity.def')
        sbi = SingularityBuildWorkItem(definition_file=def_file, force=FORCE)
        sbi.add_asset(os.path.join(sing_dir, "run_model.py"))
        return sbi

    def test_singularity_from_definition(self):
        sbi = self.get_alpine_simple_builder()
        sbi.run(wait_until_done=True)
        self.assertTrue(sbi.succeeded)
        self.assertIsNotNone(sbi.asset_collection)
        self.assertIn('image_name', sbi.image_tags)
        self.assertIn('build_context', sbi.image_tags)
        self.assertEqual(sbi.image_tags['image_name'], 'Singularity.sif')
        self.assertIn('created_by', sbi.image_tags)
        asset_file = os.path.join(os.curdir, "Singularity.sif.asset_id")
        self.assertTrue(os.path.exists(asset_file))
        os.remove(asset_file)

    def test_singularity_template(self):
        sing_dir = os.path.join(COMMON_INPUT_PATH, 'singularity', 'alpine_template')
        def_file = os.path.join(sing_dir, 'Singularity.jinja')
        sbi = SingularityBuildWorkItem(
            name=self.case_name,
            definition_file=def_file, is_template=True, force=FORCE,
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
        self.assertIn('image_name', sbi.image_tags)
        self.assertIn('created_by', sbi.image_tags)
        asset_file = os.curdir + "/Singularity.jinja.sif.asset_id"
        self.assertTrue(os.path.exists(asset_file))
        with open(asset_file, "r") as asset_fd:
            asset_file_content = asset_fd.read()
            self.assertIn('Singularity.jinja.sif:asset_id:fb0a1109-6de1-1467-f50a-4dc2cf487cf9', asset_file_content)
            asset_fd.close()
        os.remove(asset_file)

    def test_singularity_from_definition_content_alpine(self):
        sing_dir = os.path.join(COMMON_INPUT_PATH, 'singularity', 'alpine_simple')
        def_file = os.path.join(sing_dir, 'Singularity.def')
        with open(def_file, "r") as myfile:
            data = myfile.read()
            # make this test unique my changing checksum
            data = data.replace("demo idmtools builds", "demo idmtools buildss")
        sbi = SingularityBuildWorkItem(definition_content=data, force=FORCE)
        sbi.add_asset(os.path.join(sing_dir, "run_model.py"))
        sbi.run(wait_until_done=True)
        self.assertTrue(sbi.succeeded)
        self.assertIsNotNone(sbi.asset_collection)
        self.assertIn('build_context', sbi.image_tags)
        self.assertIn('image_name', sbi.image_tags)
        self.assertIn('created_by', sbi.image_tags)
