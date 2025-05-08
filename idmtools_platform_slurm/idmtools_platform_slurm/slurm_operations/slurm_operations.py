"""
Here we implement the Slurm Operations.

Copyright 2025, Gates Foundation. All rights reserved.
"""
import subprocess
from dataclasses import dataclass, field
from logging import getLogger
from typing import Union, List, Any, Type

from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools_platform_file.file_operations.file_operations import FileOperations
from idmtools_platform_slurm.assets import generate_batch, generate_script, generate_simulation_script


logger = getLogger(__name__)


@dataclass
class SlurmOperations(FileOperations):

    platform: 'SlurmPlatform'  # noqa: F821
    platform_type: Type = field(default=None)

    def create_batch_file(self, item: Union[Experiment, Simulation], max_running_jobs: int = None, retries: int = None,
                          array_batch_size: int = None, dependency: bool = True, **kwargs) -> None:
        """
        Create batch file.
        Args:
            item: the item to build batch file for
            kwargs: keyword arguments used to expand functionality.
        Returns:
            None
        """
        if isinstance(item, Experiment):
            generate_batch(self.platform, item, max_running_jobs, array_batch_size, dependency)
            generate_script(self.platform, item, max_running_jobs)
        elif isinstance(item, Simulation):
            generate_simulation_script(self.platform, item, retries)
        else:
            raise NotImplementedError(f"{item.__class__.__name__} is not supported for batch creation.")

    @staticmethod
    def cancel_job(job_ids: Union[str, List[str]]) -> Any:
        """
        Cancel Slurm job for given job ids.
        Args:
            job_ids: slurm jobs id
        Returns:
            Any
        """
        if isinstance(job_ids, str):
            job_ids = [job_ids]
        logger.debug(f"Submit slurm cancel job: {job_ids}")
        result = subprocess.run(['scancel', *job_ids], stdout=subprocess.PIPE)
        stdout = "Success" if result.returncode == 0 else 'Error'
        return stdout
