import json
import os
import time
from dataclasses import dataclass
from logging import getLogger, INFO, DEBUG
from pathlib import Path
from typing import Union, Any
from uuid import uuid4

from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools_platform_slurm.slurm_operations.local_operations import LocalSlurmOperations

logger = getLogger(__name__)


def create_bridged_job(working_directory, bridged_jobs_directory, results_directory, cleanup_results: bool = True):
    """
    Creates a bridged job.

    Args:
        working_directory: Work Directory
        bridged_jobs_directory: Jobs Directory
        results_directory: Results directory
        cleanup_results: Should we clean up results file

    Returns:
        Result from job run
    """
    bridged_id = str(uuid4())
    jn = Path(bridged_jobs_directory).joinpath(f'{bridged_id}.json')
    rf = Path(results_directory).joinpath(f'{bridged_id}.json.result')
    with open(jn, "w") as jout:
        info = dict(command='sbatch', working_directory=str(working_directory))
        if logger.isEnabledFor(DEBUG):
            logger.debug(f"Requesting job: {jn} in {working_directory}")
        json.dump(info, jout)

    tries = 0
    while tries < 15:
        time.sleep(1)
        if Path(rf).exists():
            if logger.isEnabledFor(DEBUG):
                logger.debug(f"Found result job: {rf}")
            with open(rf, 'r') as rin:
                result = json.load(rin)
            if cleanup_results:
                try:
                    if logger.isEnabledFor(DEBUG):
                        logger.debug(f"Removing result: {rf}")
                    os.unlink(rf)
                except:
                    pass
            return result['output']
        tries += 1
    if logger.isEnabledFor(DEBUG):
        logger.debug(f"Failed to get result from bridge")
    return "FAILED: Bridge never reported result"


@dataclass
class BridgedLocalSlurmOperations(LocalSlurmOperations):

    def __post_init__(self):
        if not self.platform.bridged_jobs_directory.exists():
            if logger.isEnabledFor(INFO):
                logger.info(f'Creating directory {self.platform.bridged_jobs_directory}')
            if not isinstance(self.platform.bridged_jobs_directory, Path):
                self.platform.bridged_jobs_directory = Path(self.platform.bridged_jobs_directory)
            self.platform.bridged_jobs_directory.mkdir(parents=True, exist_ok=True)

    def submit_job(self, item: Union[Experiment, Simulation], **kwargs) -> Any:
        """
        Submit a Slurm job.
        Args:
            item: idmtools Experiment or Simulation
            kwargs: keyword arguments used to expand functionality
        Returns:
            Any
        """
        if isinstance(item, Experiment):
            working_directory = self.get_directory(item)
            return create_bridged_job(working_directory, self.platform.bridged_jobs_directory, self.platform.bridged_results_directory)
        elif isinstance(item, Simulation):
            pass
        else:
            raise NotImplementedError(f"Submit job is not implemented on SlurmPlatform.")
