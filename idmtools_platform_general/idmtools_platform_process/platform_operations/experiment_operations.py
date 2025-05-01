"""
Here we implement the ProcessPlatform experiment operations.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import os
from pathlib import Path
from dataclasses import dataclass
from idmtools.entities.experiment import Experiment
from idmtools_platform_file.platform_operations.experiment_operations import FilePlatformExperimentOperations
from logging import getLogger

user_logger = getLogger('user')


@dataclass
class ProcessPlatformExperimentOperations(FilePlatformExperimentOperations):
    """
    Experiment Operations for Process Platform.
    """

    def platform_run_item(self, experiment: Experiment, **kwargs):
        """
        Run experiment.
        Args:
            experiment: idmtools Experiment
            kwargs: keyword arguments used to expand functionality
        Returns:
            None
        """
        # Ensure parent
        super().platform_run_item(experiment, **kwargs)

    def post_run_item(self, experiment: Experiment, **kwargs):
        """
        Trigger right after commissioning experiment on platform.

        Args:
            experiment: Experiment just commissioned
            kwargs: keyword arguments used to expand functionality
        Returns:
            None
        """
        super().post_run_item(experiment, **kwargs)
        user_logger.info(
            f'\nYou may try the following command to check simulations running status: \n  idmtools file {os.path.abspath(self.platform.job_directory)} status --exp-id {experiment.id}')
