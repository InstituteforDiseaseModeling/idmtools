import unittest
from unittest.mock import patch
from pathlib import Path
from idmtools_platform_file.platform_operations.utils import validate_file_copy_path_length, \
    validate_folder_files_path_length, validate_file_path_length

current_directory = Path.cwd()


class TestValidateFolderFilesPathLength(unittest.TestCase):

    @patch('idmtools_platform_file.platform_operations.utils.is_windows', return_value=True)
    @patch('idmtools_platform_file.platform_operations.utils.is_long_paths_enabled', return_value=False)
    @patch('idmtools_platform_file.platform_operations.utils.get_max_filepath', return_value='a' * 200)
    @patch('idmtools_platform_file.platform_operations.utils.user_logger')
    def test_validate_folder_files_path_length_less_than_limit(self, mock_user_logger, mock_get_max_filepath, mock_is_long_paths_enabled, mock_is_windows):
        common_asset_dir = 'some/common/asset/dir'
        link_dir = 'some/link/dir'
        validate_folder_files_path_length(common_asset_dir, link_dir, limit=256)
        mock_user_logger.assert_not_called()

    @patch('idmtools_platform_file.platform_operations.utils.is_windows', return_value=True)
    @patch('idmtools_platform_file.platform_operations.utils.is_long_paths_enabled', return_value=False)
    @patch('idmtools_platform_file.platform_operations.utils.get_max_filepath', return_value='a' * 270)
    @patch('idmtools_platform_file.platform_operations.utils.user_logger')
    def test_validate_folder_files_path_length_over_limit(self, mock_user_logger, mock_get_max_filepath, mock_is_long_paths_enabled, mock_is_windows):
        common_asset_dir = 'some/common/asset/dir'
        link_dir = 'some/link/dir'
        with self.assertRaises(SystemExit):
            validate_folder_files_path_length(common_asset_dir, link_dir, limit=256)
        self.assertIn('File path length too long', mock_user_logger.warning.call_args_list[0].args[0])
        self.assertIn('You may want to adjust your job_directory location, short Experiment name or Suite name to reduce the file path length. Or you can enable long paths in Windows,', mock_user_logger.warning.call_args_list[1].args[0])

    @patch('idmtools_platform_file.platform_operations.utils.is_windows', return_value=True)
    @patch('idmtools_platform_file.platform_operations.utils.is_long_paths_enabled', return_value=False)
    @patch('idmtools_platform_file.platform_operations.utils.get_max_filepath', return_value=None)
    @patch('idmtools_platform_file.platform_operations.utils.validate_file_path_length')
    @patch('idmtools_platform_file.platform_operations.utils.user_logger')
    def test_validate_folder_files_path_length_no_asset_path(self, mock_user_logger, mock_validate_file_path_length, mock_get_max_filepath, mock_is_long_paths_enabled, mock_is_windows):
        common_asset_dir = 'some/common/asset/dir'
        link_dir = 'some/link/dir'
        validate_folder_files_path_length(common_asset_dir, link_dir, limit=256)
        mock_user_logger.assert_not_called()
        mock_validate_file_path_length.assert_called_once_with(link_dir, 256)

    @patch('idmtools_platform_file.platform_operations.utils.is_windows', return_value=True)
    @patch('idmtools_platform_file.platform_operations.utils.is_long_paths_enabled', return_value=True)
    @patch('idmtools_platform_file.platform_operations.utils.validate_file_path_length')
    def test_file_copy_path_length_with_long_paths_enabled(self, mock_validate_file_path_length, mock_is_long_paths_enabled, mock_is_windows):
        src = 'some/source/file.txt'
        dest = 'some/destination/dir'
        validate_file_copy_path_length(src, dest, limit=256)
        mock_validate_file_path_length.assert_not_called()

    @patch('idmtools_platform_file.platform_operations.utils.is_windows', return_value=False)
    @patch('idmtools_platform_file.platform_operations.utils.is_long_paths_enabled')
    @patch('idmtools_platform_file.platform_operations.utils.validate_file_path_length')
    def test_file_copy_path_length_non_windows(self, mock_validate_file_path_length, mock_is_long_paths_enabled, mock_is_windows):
        src = 'some/source/file.txt'
        dest = 'some/destination/dir'
        validate_file_copy_path_length(src, dest, limit=256)
        mock_validate_file_path_length.assert_not_called()
        mock_is_long_paths_enabled.assert_not_called()

    @patch('idmtools_platform_file.platform_operations.utils.is_windows', return_value=True)
    @patch('idmtools_platform_file.platform_operations.utils.is_long_paths_enabled', return_value=False)
    @patch('idmtools_platform_file.platform_operations.utils.validate_file_path_length')
    def test_file_copy_path_length_with_long_filename(self, mock_validate_file_path_length, mock_is_long_paths_enabled, mock_is_windows):
        src = 'some/source/' + 'a' * 250 + '.txt'
        dest = 'some/destination/dir'
        validate_file_copy_path_length(src, dest, limit=256)
        mock_validate_file_path_length.assert_called_once_with(Path(dest) / ('a' * 250 + '.txt'), 256)

    @patch('idmtools_platform_file.platform_operations.utils.is_windows', return_value=True)
    @patch('idmtools_platform_file.platform_operations.utils.is_long_paths_enabled', return_value=False)
    @patch('idmtools_platform_file.platform_operations.utils.user_logger')
    def test_validate_file_path(self, mock_user_logger, mock_is_long_paths_enabled, mock_is_windows):
        file_path = 'some/source/' + 'a' * 250 + '.txt'
        with self.assertRaises(SystemExit):
            validate_file_path_length(file_path)
        self.assertIn('File path length too long', mock_user_logger.warning.call_args_list[0].args[0])
        self.assertIn('You may want to adjust your job_directory location, short Experiment name or Suite name to reduce the file path length. Or you can enable long paths in Windows,', mock_user_logger.warning.call_args_list[1].args[0])

        # verify file_path is Path instead of string case
        file_path = 'some/source/' + 'a' * 25 + '.txt'  # length less than 256
        file_path = Path(file_path)
        validate_file_path_length(file_path)
        mock_user_logger.assert_not_called()

