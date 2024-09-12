import unittest
from unittest.mock import patch
import pytest
from idmtools.core.platform_factory import Platform
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment


@pytest.mark.serial
class TestPlatformExperiment(unittest.TestCase):
    @patch('idmtools_platform_file.platform_operations.utils.user_logger')
    def test_max_file_path(self, mock_user_logger):
        platform = Platform("Container", job_directory="dest")

        # Define task
        command = "echo 'Hello, World!'"
        task = CommandTask(command=command)
        task.transient_assets.add_asset("inputs/Assets/MyLib/functions.py")
        # Run an experiment
        experiment = Experiment.from_task(task, name='a' * 240)
        with self.assertRaises(SystemExit):
            experiment.run(wait_until_done=False)
        mock_user_logger.warning.call_args_list[0].assert_called_with("File path length too long")
        mock_user_logger.warning.call_args_list[1].assert_called_with("You may want to adjust your job_directory location")