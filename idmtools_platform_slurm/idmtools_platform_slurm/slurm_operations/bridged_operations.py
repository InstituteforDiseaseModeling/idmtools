import json
import subprocess
import time
from dataclasses import dataclass
from logging import getLogger, INFO
from pathlib import Path
from typing import Union, Any
from uuid import uuid4

from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools_platform_slurm.slurm_operations.local_operations import LocalSlurmOperations

logger = getLogger(__name__)


def create_bridged_job(working_directory, jobs_directory, results_directory):
    bridged_id = str(uuid4())
    jn = Path(jobs_directory).joinpath(f'{bridged_id}.json')
    rf = Path(results_directory).joinpath(f'{bridged_id}.json.result')
    with open(jn, "w") as jout:
        info = dict(working_directory=str(working_directory))
        json.dump(info, jout)

    tries = 0
    while tries < 15:
        time.sleep(1)
        if Path(rf).exists():
            with open(rf, 'r') as rin:
                result = rin.read()
            return result
        tries += 1
    return "FAILED: Bridge never reported result"


@dataclass
class BridgedLocalSlurmOperations(LocalSlurmOperations):
    jobs_directory = Path.home().joinpath(".idmtools").joinpath("singularity-bridge")
    results_directory = Path.home().joinpath(".idmtools").joinpath("singularity-bridge").joinpath("results")

    def __post_init__(self):
        if not self.jobs_directory.exists():
            if logger.isEnabledFor(INFO):
                logger.info(f'Creating directory {self.jobs_directory}')
            self.jobs_directory.mkdir(parents=True, exist_ok=True)

    def submit_job(self, item: Union[Experiment, Simulation], **kwargs) -> Any:
        """
        Submit a Slurm job.
        Args:
            item: idmtools Experiment or Simulation
            kwargs: keyword arguments used to expand functionality
        Returns:
            Any
        """
        dry_run = kwargs.get('dry_run', False)
        if isinstance(item, Experiment):
            if not dry_run:
                working_directory = self.get_directory(item)

                return create_bridged_job(working_directory, self.jobs_directory, self.results_directory)
        elif isinstance(item, Simulation):
            pass
        else:
            raise NotImplementedError(f"Submit job is not implemented on SlurmPlatform.")
