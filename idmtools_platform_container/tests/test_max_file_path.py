import unittest
from unittest.mock import patch
import pytest

from idmtools.core import EntityStatus
from idmtools.core.platform_factory import Platform
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment


@pytest.mark.serial
class TestPlatformExperiment(unittest.TestCase):
    def test_max_file_path_too_long(self):
        platform = Platform("Container", job_directory="dest")

        # Define task
        command = "echo 'Hello, World!'"
        task = CommandTask(command=command)
        task.transient_assets.add_asset("inputs/Assets/MyLib/functions.py")
        # Run an experiment
        experiment = Experiment.from_task(task, name='a' * 210)
        experiment.run(wait_until_done=False)
        self.assertIn(f"e_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa_{experiment.id}", str(experiment.directory))

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

