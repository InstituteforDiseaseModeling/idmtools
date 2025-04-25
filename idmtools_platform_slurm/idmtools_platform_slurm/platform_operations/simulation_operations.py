"""
Here we implement the SlurmPlatform simulation operations.

Copyright 2025, Gates Foundation. All rights reserved.
"""
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any
from idmtools.core import ItemType, EntityStatus
from idmtools_platform_file.platform_operations.simulation_operations import FilePlatformSimulationOperations
from logging import getLogger

logger = getLogger(__name__)
user_logger = getLogger('user')

if TYPE_CHECKING:
    from idmtools_platform_slurm.slurm_platform import SlurmPlatform

logger = getLogger(__name__)


@dataclass
class SlurmPlatformSimulationOperations(FilePlatformSimulationOperations):
    platform: 'SlurmPlatform'  # noqa: F821

    def platform_cancel(self, sim_id: str, force: bool = False) -> Any:
        """
        Cancel platform simulation's slurm job.
        Args:
            sim_id: simulation id
            force: bool, True/False
        Returns:
            Any
        """
        sim = self.platform.get_item(sim_id, ItemType.SIMULATION, raw=False)
        if force or sim.status == EntityStatus.RUNNING:
            logger.debug(f"cancel slurm job for simulation: {sim_id}...")
            job_id = self.platform.get_job_id(sim_id, ItemType.SIMULATION)
            if job_id is None:
                logger.debug(f"Slurm job for simulation: {sim_id} is not available!")
                return
            else:
                result = self.platform._slurm_op.cancel_job(job_id)
                user_logger.info(f"Cancel Simulation: {sim_id}: {result}")
                return result
        else:
            user_logger.info(f"Simulation {sim_id} is not running, no cancel needed...")
