"""
Here we implement the ContainerPlatform simulation operations.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import subprocess
from dataclasses import dataclass
from typing import NoReturn, Dict
from idmtools.core import ItemType
from idmtools_platform_file.platform_operations.simulation_operations import FilePlatformSimulationOperations
from idmtools_platform_container.container_operations.docker_operations import find_running_job
from logging import getLogger

logger = getLogger(__name__)
user_logger = getLogger('user')


@dataclass
class ContainerPlatformSimulationOperations(FilePlatformSimulationOperations):
    """
    Simulation Operation for Container Platform.
    """

    def platform_cancel(self, sim_id: str, force: bool = False) -> NoReturn:
        """
        Cancel platform simulation's container job.
        Args:
            sim_id: simulation id
            force: bool, True/False
        Returns:
            NoReturn
        """
        job = find_running_job(self.platform, sim_id)
        if job:
            if job.item_type != ItemType.SIMULATION:
                pass
            user_logger.debug(
                f"{job.item_type.name} {sim_id} is running on Container {job.container_id}.")
            kill_cmd = f"docker exec {job.container_id} kill -9 {job.job_id}"
            result = subprocess.run(kill_cmd, shell=True, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                print(f"Successfully killed {job.item_type.name} {sim_id}")
            else:
                print(f"Error killing {job.item_type.name} {sim_id}: {result.stderr}")
        else:
            user_logger.info(f"Simulation {sim_id} is not running, no cancel needed...")

    def create_sim_directory_map(self, simulation_id: str) -> Dict:
        """
        Build simulation working directory mapping.
        Args:
            simulation_id: simulation id

        Returns:
            Dict of simulation id as key and working dir as value
        """
        sim = self.platform.get_item(simulation_id, ItemType.SIMULATION, raw=False)
        return {sim.id: str(self.platform.get_container_directory(sim))}
