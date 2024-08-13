"""
Here we implement the ContainerPlatform experiment operations.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import shutil
import subprocess
from dataclasses import dataclass
from typing import NoReturn
from idmtools.entities.experiment import Experiment
from idmtools_platform_file.platform_operations.experiment_operations import FilePlatformExperimentOperations
from idmtools_platform_container.container_operations.docker_operations import find_running_job
from logging import getLogger

logger = getLogger(__name__)
user_logger = getLogger('user')


@dataclass
class ContainerPlatformExperimentOperations(FilePlatformExperimentOperations):
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
        super().platform_run_item(experiment, **kwargs)
        # Commission
        self.platform.submit_job(experiment, **kwargs)

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
        dry_run = kwargs.get('dry_run', False)
        if not dry_run:
            user_logger.info(f"\nContainer ID: {self.platform.container_id}")
            user_logger.info(
                f'\nYou may try the following command to check simulations running status: \n  idmtools container status {experiment.id}')

    def platform_cancel(self, experiment_id: str) -> NoReturn:
        """
        Cancel platform experiment's container job.
        Args:
            experiment_id: Experiment ID
        Returns:
            No Return
        """
        job = find_running_job(experiment_id)
        if job:
            logger.debug(
                f"{job.item_type.name} {experiment_id} is running on Container {job.container_id}.")
            kill_cmd = f"docker exec {job.container_id} pkill -TERM -g {job.job_id}"
            result = subprocess.run(kill_cmd, shell=True, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                logger.debug(f"Successfully killed {job.item_type.name} {experiment_id}")
            else:
                logger.debug(f"Error killing {job.item_type.name} {experiment_id}: {result.stderr}")
        else:
            logger.debug(f"Experiment {experiment_id} is not running, no cancel needed...")

    def platform_delete(self, experiment_id: str) -> NoReturn:
        """
        Delete platform experiment.
        Args:
            experiment_id: Experiment ID
        Returns:
            No Return
        """
        from idmtools_platform_container.utils.job_history import JobHistory
        job = JobHistory.get_job(experiment_id)
        exp_dir = job['EXPERIMENT_DIR']
        try:
            logger.debug(f"Deleting experiment {experiment_id}")
            shutil.rmtree(exp_dir)
            # Delete the job history
            logger.debug(f"Deleting job history {experiment_id}")
            JobHistory.delete(experiment_id)
        except RuntimeError:
            logger.debug(f"Could not delete the associated experiment {experiment_id}")
