"""
Here we implement the Slurm Operations.

Copyright 2025, Gates Foundation. All rights reserved.
"""
import subprocess
from dataclasses import dataclass, field
from logging import getLogger
from pathlib import Path
from typing import Union, List, Any, Type

from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools.utils.decorators import check_symlink_capabilities
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

    @check_symlink_capabilities
    def link_file(self, target: Union[Path, str], link: Union[Path, str]) -> None:
        """
        Link files.
        Args:
            target: the source file path
            link: the file path
        Returns:
            None
        """
        target = Path(target).absolute()
        link = Path(link).absolute()
        link.symlink_to(target)

    @check_symlink_capabilities
    def link_dir(self, target: Union[Path, str], link: Union[Path, str]) -> None:
        """
        Link directory/files.
        Args:
            target: the source folder path.
            link: the folder path
        Returns:
            None
        """
        target = Path(target).absolute()
        link = Path(link).absolute()
        link.symlink_to(target)

    def submit_job(self, item: Union[Experiment, Simulation], **kwargs) -> None:
        """
        Submit a Slurm job.
        Args:
            item: idmtools Experiment or Simulation
            kwargs: keyword arguments used to expand functionality
        Returns:
            None
        """
        if isinstance(item, Experiment):
            working_directory = self.get_directory(item)
            subprocess.run(['bash', 'batch.sh'], stdout=subprocess.PIPE, cwd=str(working_directory))
        elif isinstance(item, Simulation):
            pass
        else:
            raise NotImplementedError(f"Submit job is not implemented on SlurmPlatform.")

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