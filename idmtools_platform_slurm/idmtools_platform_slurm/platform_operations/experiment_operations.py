"""
Here we implement the SlurmPlatform experiment operations.

Copyright 2025, Gates Foundation. All rights reserved.
"""
import os
from pathlib import Path
from dataclasses import dataclass
from typing import TYPE_CHECKING
from idmtools.core import EntityStatus
from idmtools.core import ItemType
from idmtools.entities.experiment import Experiment
from idmtools_platform_file.platform_operations.experiment_operations import FilePlatformExperimentOperations
from logging import getLogger


logger = getLogger(__name__)
user_logger = getLogger('user')

if TYPE_CHECKING:
    from idmtools_platform_slurm.slurm_platform import SlurmPlatform


@dataclass
class SlurmPlatformExperimentOperations(FilePlatformExperimentOperations):
    platform: 'SlurmPlatform'  # noqa: F821
    RUN_SIMULATION_SCRIPT_PATH = Path(__file__).parent.parent.joinpath('assets/run_simulation.sh')

    def platform_run_item(self, experiment: Experiment, dry_run: bool = False, **kwargs):
        """
        Run experiment.
        Args:
            experiment: idmtools Experiment
            dry_run: True/False
            kwargs: keyword arguments used to expand functionality
        Returns:
            None
        """
        # Ensure parent
        super().platform_run_item(experiment, **kwargs)
        # Commission
        if not dry_run:
            self.platform.submit_job(experiment, **kwargs)

    def refresh_status(self, experiment: Experiment, **kwargs):
        """
        Refresh status of experiment.
        Args:
            experiment: idmtools Experiment
            kwargs: keyword arguments used to expand functionality
        Returns:
            Dict of simulation id as key and working dir as value
        """
        # Check if file job_id.txt exists
        job_id_path = self.platform.get_directory(experiment).joinpath('job_id.txt')
        if not job_id_path.exists():
            logger.debug(f'job_id is not available for experiment: {experiment.id}')
            return

        # Refresh status for each simulation
        for sim in experiment.simulations:
            sim.status = self.platform.get_simulation_status(sim.id, **kwargs)

    def platform_cancel(self, experiment_id: str, force: bool = True) -> None:
        """
        Cancel platform experiment's slurm job.
        Args:
            experiment_id: experiment id
            force: bool, True/False
        Returns:
            Any
        """
        experiment = self.platform.get_item(experiment_id, ItemType.EXPERIMENT, raw=False)
        if force or experiment.status == EntityStatus.RUNNING:
            logger.debug(f"cancel slurm job for experiment: {experiment_id}...")
            job_id = self.platform.get_job_id(experiment_id, ItemType.EXPERIMENT)
            if job_id is None:
                logger.debug(f"Slurm job for experiment: {experiment_id} is not available!")
            else:
                result = self.platform._op_client.cancel_job(job_id)
                user_logger.info(f"Cancel Experiment {experiment_id}: {result}")
        else:
            user_logger.info(f"Experiment {experiment_id} is not running, no cancel needed...")

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

        job_ids = self.platform.get_job_id(experiment.id, ItemType.EXPERIMENT)
        if job_ids is None:
            logger.debug(f"Slurm job for experiment: {experiment.id} is not available!")
            user_logger.info("Slurm Job Ids: None")
        else:
            job_ids = [f'{" ".ljust(3)}{id}' for id in job_ids]
            user_logger.info(f"Slurm Job Ids ({len(job_ids)}):")
            user_logger.info('\n'.join(job_ids))

        user_logger.info(
            f'\nYou may try the following command to check simulations running status: \n  idmtools slurm {os.path.abspath(self.platform.job_directory)} status --exp-id {experiment.id}')
