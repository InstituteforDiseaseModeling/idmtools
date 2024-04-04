import os
import unittest
from unittest.mock import patch

import allure
import pytest
from unittest import mock
from idmtools_test.utils.cli import run_command
from idmtools.assets import AssetCollection
from idmtools_platform_comps.utils.package_version import get_latest_version, \
    fetch_package_versions, get_highest_version, get_latest_compatible_version
from idmtools_test import COMMON_INPUT_PATH

wheel_file_1 = os.path.join(COMMON_INPUT_PATH, 'simple_load_lib_example', 'fake_wheel_file_a.whl')
wheel_file_2 = os.path.join(COMMON_INPUT_PATH, 'simple_load_lib_example', 'fake_wheel_file_b.whl')


@pytest.mark.comps
@allure.story("CLI")
@pytest.mark.serial
class TestPackageVersionCLI(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        env = dict(
            # ensure cli commands use the print logger so output is captured
            IDMTOOLS_LOGGING_USE_COLORED_LOGS='f',
            # disable printing the block here
            SHOW_PLATFORM_CONFIG='f',
            # Hide dev warnings
            HIDE_DEV_WARNING='t'
        )
        # default options for cli commands
        cls.default_opts = dict(
            mix_stderr=False,
            env=env
        )

    @allure.feature("req2ac")
    def test_create_ac_with_req2ac(self):
        # cli: idmtools comps SLURM2 req2ac --asset_tag test:123 --pkg astor~=0.7.0
        # run req2ac to get ac_id
        result = run_command(
            'comps', 'SLURMSTAGE', 'req2ac', '--asset_tag', 'test:123',
            '--pkg', 'astor~=0.7.0', **self.default_opts)
        self.assertTrue(result.exit_code == 0, msg=result.output)
        print(result.stdout)
        ac_id = result.stdout.strip().split("\n")
        self.assertGreaterEqual(len(ac_id), 1, msg=f"Could not find ac_id in {ac_id}")
        ac_id = ac_id[-1].strip()

        # run ac-exist to verify ac
        ac = AssetCollection.from_id(ac_id, as_copy=True)
        assets = [asset for asset in ac.assets if "astor-0.7.1" in asset.relative_path]
        self.assertTrue(len(assets) > 0)

    @allure.feature("req2ac")
    @pytest.mark.serial
    def test_ac_exist_with_req2ac(self):
        # cli: idmtools comps SLURM2 ac-exist --pkg astor~=0.7.0
        # run req2ac to get ac_id
        result1 = run_command('comps', 'SLURMSTAGE', 'req2ac', '--pkg', 'astor~=0.7.0', **self.default_opts)
        self.assertTrue(result1.exit_code == 0, msg=result1.output)
        print(result1.stdout)
        ac_id = result1.stdout.strip().split("\n")
        self.assertGreaterEqual(len(ac_id), 1, msg=f"Could not find ac_id in {ac_id}")
        ac_id = ac_id[-1].strip()

        # run ac-exist to verify ac
        result2 = run_command('comps', 'SLURMSTAGE', 'ac-exist', '--pkg', 'astor~=0.7.0', **self.default_opts)
        self.assertTrue(result2.exit_code == 0, msg=result2.output)
        print(result2.stdout)
        self.assertIn(ac_id, result2.output)
        ac = AssetCollection.from_id(ac_id, as_copy=True)
        assets = [asset for asset in ac.assets if "astor-0.7.1" in asset.relative_path]
        self.assertTrue(len(assets) > 0)

    @allure.feature("req2ac")
    def test_ac_not_exist_with_req2ac(self):
        # cli: idmtools comps SLURM2 ac-exist --pkg pytest==3.0.0
        result = run_command('comps', 'SLURMSTAGE', 'ac-exist', '--pkg', 'pytest==3.0.0', **self.default_opts)
        self.assertTrue(result.exit_code == 0, msg=result.output)
        self.assertIn("AC doesn't exist", result.output)

    @allure.feature("req2ac")
    def test_req2ac_latest_version(self):
        # cli: idmtools package latest-version --name pytest
        test_versions = ['10.0.0', '0.8.1', '0.8.0', '0.7.1', '0.7.0', '0.6.2', '0.6.1', '0.6', '0.5', '0.4.1', '0.4',
                         '0.3', '0.2.1', '0.2', '0.1']
        with mock.patch('idmtools_platform_comps.utils.package_version.fetch_versions_from_server',
                        return_value=test_versions) as mock_fetch:
            result = run_command('package', 'latest-version', '--name', 'astor', **self.default_opts)
            self.assertTrue(result.exit_code == 0, msg=result.output)
            self.assertTrue("10.0.0", result.output)

    @allure.feature("req2ac")
    def test_req2ac_list_versions(self):
        # cli: idmtools package list-versions --name astor
        import re
        test_versions = ['10.0.0', '0.8.1', '0.8.0', '0.7.1', '0.7.0', '0.6.2', '0.6.1', '0.6', '0.5', '0.4.1', '0.4',
                         '0.3', '0.2.1', '0.2', '0.1']
        with mock.patch('idmtools_platform_comps.utils.package_version.fetch_versions_from_server',
                        return_value=test_versions) as mock_fetch:
            result = run_command('package', 'list-versions', '--name', 'astor', **self.default_opts)
            self.assertTrue(result.exit_code == 0, msg=result.output)
            output_str = result.output
            actual_versions = re.sub(r'["[\]\'\n ]', '', output_str).split(',')
            self.assertListEqual(actual_versions, test_versions)

    @allure.feature("req2ac")
    def test_req2ac_compatible_version(self):
        # cli: idmtools package  compatible-version --name astor base_version 0.7.0
        result = run_command(
            'package', 'compatible-version',
            '--name', 'astor',
            '--base_version', '0.7.0',
            **self.default_opts
        )
        self.assertTrue(result.exit_code == 0, msg=result.output)
        self.assertTrue("0.7.1", result.output)

    @allure.feature("req2ac")
    def test_req2ac_checksum(self):
        # cli: idmtools package checksum --pkg astor==0.8.1
        result = run_command('package', 'checksum', '--pkg', 'astor==0.8.1', **self.default_opts)
        self.assertTrue(result.exit_code == 0, msg=result.output)
        self.assertTrue("3a620d2dc5e26856a9d4442f33785a0a", result.output)

    @allure.feature("req2ac")
    def test_req2ac_updated_requirements(self):
        # cli: idmtools package updated-requirements --pkg astor~=0.7.0
        result = run_command('package', 'updated-requirements', '--pkg', 'astor~=0.7.0', **self.default_opts)
        self.assertTrue(result.exit_code == 0, msg=result.output)
        self.assertTrue("astor==0.7.1", result.stdout_bytes.decode('utf-8'))

    @allure.feature("req2ac")
    def test_req2ac_checksum_pkg_order(self):
        # cli: idmtools package checksum --pkg astor==0.8.1 --pkg idmtools==1.6.2
        result1 = run_command(
            'package', 'checksum',
            '--pkg', 'astor==0.8.1',
            '--pkg', 'idmtools==1.6.2',
            **self.default_opts
        )
        self.assertTrue(result1.exit_code == 0, msg=result1.output)
        result2 = run_command(
            'package', 'checksum',
            '--pkg', 'idmtools==1.6.2',
            '--pkg', 'astor==0.8.1',
            **self.default_opts
        )
        self.assertTrue(result2.exit_code == 0, msg=result2.output)
        self.assertEqual(result1.output, result2.output)
        self.assertTrue("8c815fe17f8d7dfeb790b5d0041b288a", result1.output)

    @allure.feature("req2ac")
    def test_req2ac_checksum_wheels_order(self):
        # cli: idmtools package checksum --wheel wheel_file_1 --wheel wheel_file_2
        result1 = run_command(
            'package', 'checksum',
            '--wheel', wheel_file_1,
            '--wheel', wheel_file_2,
            **self.default_opts
        )
        self.assertTrue(result1.exit_code == 0, msg=result1.output)
        result2 = run_command(
            'package', 'checksum', '--wheel', wheel_file_2,
            '--wheel', wheel_file_1,
            **self.default_opts
        )
        self.assertTrue(result2.exit_code == 0, msg=result2.output)
        self.assertEqual(result1.output, result2.output)
        self.assertTrue("d2e204cfbf40e78d6b18fe862f422512", result1.output)

    @allure.feature("req2ac")
    def test_req2ac_updated_requirements_wheels_order(self):
        # cli: idmtools package updated-requirements --wheel wheel_file_1 --wheel wheel_file_2
        result1 = run_command(
            'package', 'updated-requirements', '--wheel', wheel_file_1,
            '--wheel', wheel_file_2, **self.default_opts
        )
        self.assertTrue(result1.exit_code == 0, msg=result1.output)
        result2 = run_command(
            'package', 'updated-requirements', '--wheel', wheel_file_2,
            '--wheel', wheel_file_1, **self.default_opts
        )
        self.assertTrue(result2.exit_code == 0, msg=result2.output)
        self.assertEqual(result1.output, result2.output)
        self.assertTrue("d2e204cfbf40e78d6b18fe862f422512", result1.output)
        self.assertTrue('Assets/fake_wheel_file_a.whl\nAssets/fake_wheel_file_b.whl\n',
                        result1.stdout_bytes.decode('utf-8'))

    @allure.feature("req2ac")
    def test_req2ac_updated_requirements_pgk_order(self):
        # cli: idmtools package updated-requirements --wheel wheel_file_1 --wheel wheel_file_2
        result1 = run_command(
            'package', 'updated-requirements',
            '--pkg', 'astor~=0.7.0', '--pkg', 'idmtools==1.6.2', **self.default_opts
        )
        self.assertTrue(result1.exit_code == 0, msg=result1.output)
        result2 = run_command(
            'package', 'updated-requirements',
            '--pkg', 'idmtools==1.6.2', '--pkg', 'astor~=0.7.0', **self.default_opts)
        self.assertTrue(result2.exit_code == 0, msg=result2.output)
        self.assertEqual(result1.output, result2.output)
        self.assertTrue("astor==0.7.1\nidmtools==1.6.2\n", result1.output)
        self.assertTrue("astor==0.7.1\nidmtools==1.6.2\n", result1.stdout_bytes.decode('utf-8'))

    @allure.feature("req2ac")
    def test_req2ac_checksum_pkg_wheels_order(self):
        # cli: idmtools package updated-requirements --pkg astor==0.8.1 --pkg idmtools==1.6.2 --wheel wheel_file_1 --wheel wheel_file_2
        result1 = run_command(
            'package', 'checksum', '--pkg', 'astor==0.8.1', '--pkg', 'idmtools==1.6.2',
            '--wheel', wheel_file_1, '--wheel', wheel_file_2, **self.default_opts
        )
        self.assertTrue(result1.exit_code == 0, msg=result1.output)
        result2 = run_command(
            'package', 'checksum', '--pkg', 'idmtools==1.6.2', '--pkg', 'astor==0.8.1',
            '--wheel', wheel_file_2, '--wheel', wheel_file_1, **self.default_opts
        )
        self.assertTrue(result2.exit_code == 0, msg=result2.output)
        self.assertEqual(result1.output, result2.output)
        self.assertTrue("8d50bf1f9fc60b806d9816bf5809748d", result1.output)

    @allure.feature("req2ac")
    def test_req2ac_updated_requirements_pkg_wheels_order(self):
        # cli: idmtools package updated-requirements --pkg astor==0.8.1 --pkg idmtools==1.6.2 --wheel wheel_file_1 --wheel wheel_file_2
        result1 = run_command(
            'package', 'updated-requirements', '--pkg', 'astor==0.8.1',
            '--pkg', 'idmtools==1.6.2', '--wheel', wheel_file_1,
            '--wheel', wheel_file_2, **self.default_opts
        )
        self.assertTrue(result1.exit_code == 0, msg=result1.output)
        result2 = run_command(
            'package', 'updated-requirements', '--pkg', 'idmtools==1.6.2',
            '--pkg', 'astor==0.8.1', '--wheel', wheel_file_2,
            '--wheel', wheel_file_1, **self.default_opts
        )
        self.assertTrue(result2.exit_code == 0, msg=result2.output)
        self.assertEqual(result1.output, result2.output)
        self.assertTrue("8d50bf1f9fc60b806d9816bf5809748d", result1.output)
        self.assertTrue('astor==0.8.1\nidmtools==1.6.2\nAssets/fake_wheel_file_a.whl\nAssets/fake_wheel_file_b.whl\n',
                        result1.stdout_bytes.decode('utf-8'))

    @pytest.mark.serial
    def test_get_highest_version(self):
        test_versions = ['10.0.0', '0.8.1', '0.8.0', '0.7.1', '0.7.0', '0.6.2', '0.6.1', '0.6', '0.5', '0.4.1', '0.4',
                         '0.3', '0.2.1', '0.2', '0.1']
        with mock.patch('idmtools_platform_comps.utils.package_version.fetch_versions_from_server',
                        return_value=test_versions) as mock_fetch:
            self.assertEqual(get_highest_version(pkg_requirement='astor<0.7.1'), '0.7.0')
            self.assertEqual(get_highest_version(pkg_requirement='astor<=0.7.1'), '0.7.1')
            self.assertEqual(get_highest_version(pkg_requirement='astor~=0.8.0'), '0.8.1')
            self.assertEqual(get_highest_version(pkg_requirement='astor>=0.8.0'), '10.0.0')
            self.assertEqual(get_highest_version(pkg_requirement='astor>0.8.0'), '10.0.0')
            self.assertEqual(get_highest_version(pkg_requirement='astor!=0.7.1'), '10.0.0')
            self.assertEqual(get_highest_version(pkg_requirement='astor==0.6'), '0.6')

    @pytest.mark.serial
    def test_get_latest_version(self):
        test_versions = ['10.0.0', '0.8.1', '0.8.0', '0.7.1', '0.7.0', '0.6.2', '0.6.1', '0.6', '0.5', '0.4.1', '0.4',
                         '0.3', '0.2.1', '0.2', '0.1']
        with mock.patch('idmtools_platform_comps.utils.package_version.fetch_versions_from_server',
                        return_value=test_versions) as mock_fetch:
            self.assertEqual(get_latest_version(pkg_name='astor'), '10.0.0')

    @pytest.mark.serial
    def test_fetch_package_versions_with_sort(self):
        test_versions = ['0.7.1', '0.8.1', '0.8.0r', '0.7.0', '0.6.2', '0.6.1', '0.6', '0.5', '0.4.1', '0.4', '0.3',
                         '0.2.1', '0.1', '0.2']
        with mock.patch('idmtools_platform_comps.utils.package_version.fetch_versions_from_server',
                        return_value=test_versions) as mock_fetch:
            expected_sorted_versions = ['0.8.1', '0.8.0r', '0.7.1', '0.7.0', '0.6.2', '0.6.1', '0.6', '0.5', '0.4.1',
                                        '0.4', '0.3', '0.2.1', '0.2', '0.1']
            self.assertEqual(fetch_package_versions(pkg_name='astor', sort=True), expected_sorted_versions)

    @pytest.mark.serial
    def test_get_latest_compatible_version(self):
        test_versions = ['8.1.1', '8.1.0', '8.0.2', '8.0.1', '8.0.0', '7.4.4', '7.4.3', '7.4.2', '7.4.1', '7.4.0', '7.3.2', '7.0.0']
        with mock.patch('idmtools_platform_comps.utils.package_version.fetch_versions_from_server',
                        return_value=test_versions) as mock_fetch:
            self.assertEqual(get_latest_compatible_version(pkg_name='pytest', base_version='7'), '7.4.4')
            self.assertEqual(get_latest_compatible_version(pkg_name='pytest', base_version='8.1'), '8.1.1')

    @pytest.mark.serial
    def test_get_latest_compatible_version_no_exist(self):
        test_versions = ['8.1.1', '8.1.0', '8.0.2', '8.0.1', '8.0.0', '7.4.4', '7.4.3', '7.4.2', '7.4.1', '7.4.0',
                         '7.3.2', '7.0.0']
        with mock.patch('idmtools_platform_comps.utils.package_version.fetch_versions_from_server',
                        return_value=test_versions) as mock_fetch:
            self.assertEqual(get_latest_compatible_version(pkg_name='pytest', base_version='10'), None)

