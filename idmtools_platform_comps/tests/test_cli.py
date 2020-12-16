import json
import os
import unittest
from contextlib import suppress
from logging import DEBUG
from pathlib import PurePath
import allure
import pytest
from idmtools.core import ItemType
from idmtools.core.logging import setup_logging
from idmtools.core.platform_factory import Platform
from idmtools_test.test_precreate_hooks import TEST_WITH_NEW_CODE
from idmtools_test.utils.cli import run_command, get_subcommands_from_help_result
from idmtools_test.utils.comps import run_package_dists
from idmtools_test.utils.decorators import run_in_temp_dir

pwd = PurePath(__file__).parent.joinpath('inputs', 'singularity_builds', 'glob_inputs')


@pytest.mark.comps
@allure.story("CLI")
class TestCompsCLI(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        # To enable this, you need to also set the env var TEST_WITH_PACKAGES to t or y
        if TEST_WITH_NEW_CODE:
            # Run package dists
            run_package_dists()

    @classmethod
    def setUpClass(cls) -> None:
        # Setup logging for cli
        os.environ['IDMTOOLS_LOGGING_USER_PRINT'] = '1'
        os.environ['IDMTOOLS_HIDE_DEV_WARNING'] = '1'
        setup_logging(level=DEBUG, force=True)
        with suppress(PermissionError):
            if os.path.exists(pwd.joinpath("singularity.id")):
                os.remove(pwd.joinpath("singularity.id"))

    @classmethod
    def tearDownClass(cls) -> None:
        # Reset Logging
        del os.environ['IDMTOOLS_LOGGING_USER_PRINT']
        del os.environ['IDMTOOLS_HIDE_DEV_WARNING']
        setup_logging(level=DEBUG, filename='idmtools.log', force=True)

    def test_subcommands_exists(self):
        result = run_command('comps', '--help')
        print(result.stdout)
        lines = get_subcommands_from_help_result(result)
        # ensure our command is in the options
        with self.subTest("test_assetize_subcommand"):
            self.assertIn('assetize-outputs', lines)
        with self.subTest("test_singularity_subcommand"):
            self.assertIn('singularity', lines)
        with self.subTest("test_login_subcommand"):
            self.assertIn('login', lines)

    @allure.feature("AssetizeOutputs")
    def test_assetize_dry_run_json(self):
        result = run_command('comps', 'Bayesian', 'assetize-outputs', '--experiment', '9311af40-1337-ea11-a2be-f0921c167861', '--dry-run', '--json', mix_stderr=False)
        self.assertTrue(result.exit_code == 0, msg=result.output)
        print(result.stdout)
        files = json.loads(result.stdout)
        self.assertEqual(36, len(files))

    @allure.feature("AssetizeOutputs")
    def test_assetize_id(self):
        fn = 'assetize.id'
        op = PurePath(__file__).parent
        if os.path.exists(op.joinpath(fn)):
            os.remove(op.joinpath(fn))
        result = run_command('comps', 'Bayesian', 'assetize-outputs', '--experiment', '9311af40-1337-ea11-a2be-f0921c167861', '--json', '--id-file', '--id-filename', fn, mix_stderr=False)
        print(result.stdout)
        self.assertTrue(result.exit_code == 0)
        files = json.loads(result.stdout)
        self.assertEqual(36, len(files))
        self.assertTrue(os.path.exists(op.joinpath(fn)))

    @allure.feature("AssetizeOutputs")
    def test_cli_error(self):
        result = run_command('comps', 'Bayesian', 'assetize-outputs', '--experiment', '9311af40-1337-ea11-a2be-f0921c167861', '--pattern', '34234234')
        print(result.stdout)
        self.assertTrue(result.exit_code == -1)
        self.assertIn("No files found with patterns specified", result.stdout)

    @allure.feature("Containers")
    def test_container_pull(self):
        result = run_command('comps', 'SLURM2', 'singularity', 'pull', 'docker://python:3.8.6', mix_stderr=False)
        print(result.stdout)
        self.assertTrue(result.exit_code == 0)
        self.assertTrue(os.path.exists("python_3.8.6.id"))

    @allure.feature("Containers")
    @run_in_temp_dir
    def test_container_build(self):
        if os.path.exists(pwd.joinpath("singularity.id")):
            os.remove(pwd.joinpath("singularity.id"))
        result = run_command('comps', 'SLURM2', 'singularity', 'build', '--common-input-glob', str(pwd.joinpath('*.txt')), str(pwd.joinpath('singularity.def')), mix_stderr=False)
        print(result.stdout)
        self.assertTrue(result.exit_code == 0)
        self.assertTrue(os.path.exists(pwd.joinpath("singularity.id")))

    @allure.feature("Containers")
    @run_in_temp_dir
    def test_container_build_force_and_workitem_id(self):
        id_files = ["builder.singularity.id", "singularity.id"]
        for file in id_files:
            if os.path.exists(pwd.joinpath(file)):
                os.remove(pwd.joinpath(file))
        result = run_command('comps', 'SLURM2', 'singularity', 'build', '--force', '--id-workitem', '--common-input-glob', str(pwd.joinpath('*.txt')), str(pwd.joinpath('singularity.def')), mix_stderr=False)
        print(result.stdout)
        self.assertTrue(result.exit_code == 0)
        for file in id_files:
            self.assertTrue(os.path.exists(pwd.joinpath(file)))

        # verify the id file
        with open(pwd.joinpath(pwd.joinpath(id_files[0])), 'r') as cin:
            content = cin.read()

        with open(pwd.joinpath(pwd.joinpath(id_files[1])), 'r') as cin:
            asset_id_content = cin.read()

        parts = content.split("::")
        self.assertTrue(len(parts) == 3)
        pl = Platform("SLURM2")
        wi = pl.get_item(parts[0], ItemType.WORKFLOW_ITEM)
        self.assertIn('WorkItem_Type', wi.tags.keys())
        self.assertEqual(wi.tags['WorkItem_Type'], 'ImageBuilderWorker')

        parts = asset_id_content.split("::")
        self.assertTrue(len(parts) == 3)
        ac = pl.get_item(parts[0], ItemType.ASSETCOLLECTION)
        self.assertIn('type', ac.tags.keys())
        self.assertIn('image_name', ac.tags.keys())
        self.assertEqual(ac.tags['type'], 'singularity')
        self.assertEqual(ac.tags['image_name'], 'singularity.sif')

        # cleanup for next test
        for file in id_files:
            os.remove(pwd.joinpath(file))
        with self.subTest("test_container_workitem_id_not_written_when_found"):
            # hit cache and ensure file is not written
            result = run_command('comps', 'SLURM2', 'singularity', 'build', '--id-workitem', '--common-input-glob', str(pwd.joinpath('*.txt')), str(pwd.joinpath('singularity.def')), mix_stderr=False)
            self.assertTrue(result.exit_code == 0)
            self.assertTrue(os.path.exists(pwd.joinpath("singularity.id")))
            self.assertFalse(os.path.exists(pwd.joinpath("builder.singularity.id")))
