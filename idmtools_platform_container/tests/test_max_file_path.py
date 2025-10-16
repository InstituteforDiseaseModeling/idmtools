import unittest
from unittest.mock import patch
import pytest
from idmtools.core.platform_factory import Platform
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment


@pytest.mark.serial
class TestPlatformExperiment(unittest.TestCase):
    @patch('idmtools_platform_file.platform_operations.utils.user_logger')
    def test_max_file_path_too_long(self, mock_user_logger):
        platform = Platform("Container", job_directory="dest")

        # Define task
        command = "echo 'Hello, World!'"
        task = CommandTask(command=command)
        task.transient_assets.add_asset("inputs/Assets/MyLib/functions.py")
        # Run an experiment
        experiment = Experiment.from_task(task, name='a' * 210)
        import platform as p
        if p.system() in ["Windows"]:
            with self.assertRaises(SystemExit):
                experiment.run(wait_until_done=False)  # Only in Windows file path is too long, raise an exception
                mock_user_logger.warning.call_args_list[0].assert_called_with("File path length too long")
                mock_user_logger.warning.call_args_list[1].assert_called_with("You may want to adjust your job_directory location")
        else:
            experiment.run(wait_until_done=False)
            mock_user_logger.warning.assert_not_called()

    @patch('idmtools_platform_file.platform_operations.utils.user_logger')
    def test_max_file_path_not_too_long(self, mock_user_logger):
        platform = Platform("Container", job_directory="dest")

        # Define task
        command = "echo 'Hello, World!'"
        task = CommandTask(command=command)
        task.transient_assets.add_asset("inputs/Assets/MyLib/functions.py")
        # Run an experiment
        experiment = Experiment.from_task(task, name='a' * 24)
        experiment.run(wait_until_done=False)
        mock_user_logger.warning.assert_not_called()

