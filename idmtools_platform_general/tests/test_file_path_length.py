import unittest
from unittest.mock import patch
from idmtools_platform_general.idmtools_platform_file.platform_operations.utils import validate_common_assets_path_length


class TestValidateCommonAssetsPathLength(unittest.TestCase):

    @patch('idmtools_platform_file.platform_operations.utils.is_windows', return_value=True)
    @patch('idmtools_platform_file.platform_operations.utils.get_max_filepath', return_value=None)
    @patch('idmtools_platform_file.platform_operations.utils.validate_file_path_length')
    def test_common_assets_path_length_with_no_assets(self, mock_validate_file_path_length, mock_get_max_filepath, mock_is_windows):
        common_asset_dir = 'some/common/asset/dir'
        link_dir = 'some/link/dir'
        validate_common_assets_path_length(common_asset_dir, link_dir, limit=256)
        mock_validate_file_path_length.assert_called_once_with(link_dir, 256)

    @patch('idmtools_platform_file.platform_operations.utils.is_windows', return_value=False)
    @patch('idmtools_platform_file.platform_operations.utils.get_max_filepath')
    @patch('idmtools_platform_file.platform_operations.utils.validate_file_path_length')
    def test_common_assets_path_length_non_windows(self, mock_validate_file_path_length, mock_get_max_filepath, mock_is_windows):
        common_asset_dir = 'some/common/asset/dir'
        link_dir = 'some/link/dir'
        validate_common_assets_path_length(common_asset_dir, link_dir, limit=256)
        mock_validate_file_path_length.assert_not_called()
        mock_get_max_filepath.assert_not_called()

    @patch('idmtools_platform_file.platform_operations.utils.is_long_paths_enabled', return_value=True)
    @patch('idmtools_platform_file.platform_operations.utils.get_max_filepath')
    @patch('idmtools_platform_file.platform_operations.utils.validate_file_path_length')
    def test_common_assets_path_length_is_long_paths_enabled(self, mock_validate_file_path_length, mock_get_max_filepath, mock_is_windows):
        common_asset_dir = 'some/common/asset/dir'
        link_dir = 'some/link/dir'
        validate_common_assets_path_length(common_asset_dir, link_dir, limit=256)
        mock_validate_file_path_length.assert_not_called()
        mock_get_max_filepath.assert_not_called()

