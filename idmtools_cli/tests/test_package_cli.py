"""Unit tests for package CLI commands.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import unittest
import os
import tempfile
from unittest.mock import patch, MagicMock, mock_open, call
from click.testing import CliRunner
from io import StringIO


class TestPackageCLI(unittest.TestCase):
    """Test cases for package CLI commands."""

    def setUp(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        # Import here to avoid circular imports
        from idmtools_cli.cli.package import package
        self.cli = package

    def tearDown(self):
        """Clean up after tests."""
        pass


class TestLatestVersionCommand(TestPackageCLI):
    """Test cases for latest_version command."""

    @patch('idmtools_platform_comps.utils.package_version_new.get_latest_version')
    def test_latest_version_success(self, mock_get_latest):
        """Test successfully getting latest version."""
        mock_get_latest.return_value = '2.5.0'
        
        result = self.runner.invoke(self.cli, ['latest-version', '--name', 'requests'])
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn('2.5.0', result.output)
        mock_get_latest.assert_called_once_with('requests')

    @patch('idmtools_platform_comps.utils.package_version_new.get_latest_version')
    def test_latest_version_missing_name(self, mock_get_latest):
        """Test latest_version without required --name option."""
        result = self.runner.invoke(self.cli, ['latest-version'])
        
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn('Missing option', result.output)
        mock_get_latest.assert_not_called()

    @patch('idmtools_platform_comps.utils.package_version_new.get_latest_version')
    def test_latest_version_with_empty_name(self, mock_get_latest):
        """Test latest_version with empty package name."""
        mock_get_latest.return_value = None
        
        result = self.runner.invoke(self.cli, ['latest-version', '--name', ''])
        
        self.assertEqual(result.exit_code, 0)
        mock_get_latest.assert_called_once_with('')

    @patch('idmtools_platform_comps.utils.package_version_new.get_latest_version')
    def test_latest_version_returns_none(self, mock_get_latest):
        """Test latest_version when no version is found."""
        mock_get_latest.return_value = None
        
        result = self.runner.invoke(self.cli, ['latest-version', '--name', 'nonexistent-package'])
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn('None', result.output)
        mock_get_latest.assert_called_once_with('nonexistent-package')


class TestCompatibleVersionCommand(TestPackageCLI):
    """Test cases for compatible_version command."""

    @patch('idmtools_platform_comps.utils.package_version_new.get_latest_compatible_version')
    def test_compatible_version_success(self, mock_get_compatible):
        """Test successfully getting compatible version."""
        mock_get_compatible.return_value = '2.5.2'
        
        result = self.runner.invoke(
            self.cli,
            ['compatible-version', '--name', 'requests', '--base_version', '2.5']
        )
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn('2.5.2', result.output)
        mock_get_compatible.assert_called_once_with('requests', '2.5')

    @patch('idmtools_platform_comps.utils.package_version_new.get_latest_compatible_version')
    def test_compatible_version_missing_name(self, mock_get_compatible):
        """Test compatible_version without required --name option."""
        result = self.runner.invoke(
            self.cli,
            ['compatible-version', '--base_version', '2.5']
        )
        
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn('Missing option', result.output)
        mock_get_compatible.assert_not_called()

    @patch('idmtools_platform_comps.utils.package_version_new.get_latest_compatible_version')
    def test_compatible_version_missing_base_version(self, mock_get_compatible):
        """Test compatible_version without required --base_version option."""
        result = self.runner.invoke(
            self.cli,
            ['compatible-version', '--name', 'requests', '--base_version', '2.35']
        )
        
        # base_version has default=None, so this should work
        self.assertEqual(result.exit_code, 0)
        mock_get_compatible.assert_called_once_with('requests', '2.35')

    @patch('idmtools_platform_comps.utils.package_version_new.get_latest_compatible_version')
    def test_compatible_version_with_post_dev_version(self, mock_get_compatible):
        """Test compatible_version with post/dev version."""
        mock_get_compatible.return_value = '1.0.0'
        
        result = self.runner.invoke(
            self.cli,
            ['compatible-version', '--name', 'mypackage', '--base_version', '1.0.0.post1.dev0']
        )
        
        self.assertEqual(result.exit_code, 0)
        mock_get_compatible.assert_called_once_with('mypackage', '1.0.0.post1.dev0')

    @patch('idmtools_platform_comps.utils.package_version_new.get_latest_compatible_version')
    def test_compatible_version_returns_none(self, mock_get_compatible):
        """Test compatible_version when no matching version found."""
        mock_get_compatible.return_value = None
        
        result = self.runner.invoke(
            self.cli,
            ['compatible-version', '--name', 'requests', '--base_version', '99.99']
        )
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn('None', result.output)


class TestListVersionsCommand(TestPackageCLI):
    """Test cases for list_versions command."""

    @patch('idmtools_platform_comps.utils.package_version_new.fetch_package_versions')
    def test_list_versions_default(self, mock_fetch):
        """Test list_versions with default options (released only)."""
        mock_fetch.return_value = ['2.5.0', '2.4.0', '2.3.0']
        
        result = self.runner.invoke(
            self.cli,
            ['list-versions', '--name', 'requests']
        )
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn('2.5.0', result.output)
        # is_released=True (not all=False → not False=True)
        mock_fetch.assert_called_once_with('requests', True)

    @patch('idmtools_platform_comps.utils.package_version_new.fetch_package_versions')
    def test_list_versions_with_all_flag(self, mock_fetch):
        """Test list_versions with --all flag (include prereleases)."""
        mock_fetch.return_value = ['2.5.0', '2.5.0rc1', '2.4.0']
        
        result = self.runner.invoke(
            self.cli,
            ['list-versions', '--name', 'requests', '--all']
        )
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn('2.5.0rc1', result.output)
        # is_released=False (not all=True → not True=False)
        mock_fetch.assert_called_once_with('requests', False)

    @patch('idmtools_platform_comps.utils.package_version_new.fetch_package_versions')
    def test_list_versions_with_no_all_flag(self, mock_fetch):
        """Test list_versions with --no-all flag (released only)."""
        mock_fetch.return_value = ['2.5.0', '2.4.0']
        
        result = self.runner.invoke(
            self.cli,
            ['list-versions', '--name', 'requests', '--no-all']
        )
        
        self.assertEqual(result.exit_code, 0)
        mock_fetch.assert_called_once_with('requests', True)

    @patch('idmtools_platform_comps.utils.package_version_new.fetch_package_versions')
    def test_list_versions_empty_result(self, mock_fetch):
        """Test list_versions when no versions found."""
        mock_fetch.return_value = []
        
        result = self.runner.invoke(
            self.cli,
            ['list-versions', '--name', 'nonexistent']
        )
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn('[]', result.output)

    @patch('idmtools_platform_comps.utils.package_version_new.fetch_package_versions')
    def test_list_versions_missing_name(self, mock_fetch):
        """Test list_versions without required --name option."""
        result = self.runner.invoke(
            self.cli,
            ['list-versions']
        )
        
        self.assertNotEqual(result.exit_code, 0)
        mock_fetch.assert_not_called()


if __name__ == '__main__':
    unittest.main(verbosity=2)
