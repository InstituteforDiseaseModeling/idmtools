"""
Here we implement the ProcessPlatform object.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import platform
import subprocess
from typing import Union, Any
from dataclasses import dataclass
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools_platform_file.file_platform import FilePlatform
from idmtools_platform_process.platform_operations.experiment_operations import ProcessPlatformExperimentOperations
from logging import getLogger

user_logger = getLogger('user')


@dataclass(repr=False)
class ProcessPlatform(FilePlatform):
    """
    Process Platform definition.
    """

    def __post_init__(self):
        super().__post_init__()
        self._experiments = ProcessPlatformExperimentOperations(platform=self)

    def submit_job(self, item: Union[Experiment, Simulation], **kwargs) -> Any:
        """
        Submit a Process job.
        Args:
            item: idmtools Experiment or Simulation
            kwargs: keyword arguments used to expand functionality
        Returns:
            Any
        """
        if platform.system() in ["Windows"]:
            user_logger.warning(
                "\n/!\\ WARNING: The current ProcessPlatform only support running Experiment/Simulation on Linux!")
            exit(-1)

        if isinstance(item, Experiment):
            working_directory = self.get_directory(item)
            result = subprocess.run(['bash', 'batch.sh'], stdout=subprocess.PIPE, cwd=str(working_directory))
            r = result.stdout.decode('utf-8').strip()
            return r
        elif isinstance(item, Simulation):
            raise NotImplementedError("submit_job directly for simulation is not implemented on ProcessPlatform.")
        else:
            raise NotImplementedError(
                f"Submit job is not implemented for {item.__class__.__name__} on ProcessPlatform.")
