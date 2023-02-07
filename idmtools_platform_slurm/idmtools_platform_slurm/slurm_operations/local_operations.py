"""
Here we implement the SlurmPlatform local operations.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import os
import shlex
import shutil
import subprocess
from dataclasses import dataclass
from logging import getLogger
from pathlib import Path
from typing import Union, Any, List
from idmtools.core import ItemType, EntityStatus
from idmtools.entities import Suite
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools_platform_slurm.assets import generate_script, generate_simulation_script
from idmtools_platform_slurm.slurm_operations.operations_interface import SlurmOperations
from idmtools_platform_slurm.slurm_operations.slurm_constants import SLURM_MAPS

logger = getLogger(__name__)


@dataclass
class LocalSlurmOperations(SlurmOperations):

    def get_directory(self, item: Union[Suite, Experiment, Simulation]) -> Path:
        """
        Get item's path.
        Args:
            item: Suite, Experiment, Simulation
        Returns:
            item file directory
        """
        if isinstance(item, Suite):
            item_dir = Path(self.platform.job_directory, item.id)
        elif isinstance(item, Experiment):
            suite_id = item.parent_id or item.suite_id
            if suite_id is None:
                raise RuntimeError("Experiment missing parent!")
            suite_dir = Path(self.platform.job_directory, str(suite_id))
            item_dir = Path(suite_dir, item.id)
        elif isinstance(item, Simulation):
            exp = item.parent
            if exp is None:
                raise RuntimeError("Simulation missing parent!")
            exp_dir = self.get_directory(exp)
            item_dir = Path(exp_dir, item.id)
        else:
            raise RuntimeError(f"Get directory is not supported for {type(item)} object on SlurmPlatform")

        return item_dir

    def get_directory_by_id(self, item_id: str, item_type: ItemType) -> Path:
        """
        Get item's path.
        Args:
            item_id: entity id (Suite, Experiment, Simulation)
            item_type: the type of items (Suite, Experiment, Simulation)
        Returns:
            item file directory
        """
        if item_type is ItemType.SIMULATION:
            pattern = f"*/*/{item_id}"
        elif item_type is ItemType.EXPERIMENT:
            pattern = f"*/{item_id}"
        elif item_type is ItemType.SUITE:
            pattern = f"{item_id}"
        else:
            raise RuntimeError(f"Unknown item type: {item_type}")

        root = Path(self.platform.job_directory)
        for item_path in root.glob(pattern=pattern):
            return item_path
        raise RuntimeError(f"Not found path for item_id: {item_id} with type: {item_type}.")

    def mk_directory(self, item: Union[Suite, Experiment, Simulation] = None, dest: Union[Path, str] = None,
                     exist_ok: bool = True) -> None:
        """
        Make a new directory.
        Args:
            item: Suite/Experiment/Simulation
            dest: the folder path
            exist_ok: True/False
        Returns:
            None
        """
        if dest is not None:
            target = Path(dest)
        elif isinstance(item, (Suite, Experiment, Simulation)):
            target = self.get_directory(item)
        else:
            raise RuntimeError('Only support Suite/Experiment/Simulation or not None dest.')
        target.mkdir(parents=True, exist_ok=exist_ok)

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

    @staticmethod
    def update_script_mode(script_path: Union[Path, str], mode: int = 0o777) -> None:
        """
        Change file mode.
        Args:
            script_path: script path
            mode: permission mode
        Returns:
            None
        """
        script_path = Path(script_path)
        script_path.chmod(mode)

    def make_command_executable(self, simulation: Simulation) -> None:
        """
        Make simulation command executable
        Args:
            simulation: idmtools Simulation
        Returns:
            None
        """
        exe = simulation.task.command.executable
        if exe == 'singularity':
            # split the command
            cmd = shlex.split(simulation.task.command.cmd.replace("\\", "/"))
            # get real executable
            exe = cmd[3]

        sim_dir = self.get_directory(simulation)
        exe_path = sim_dir.joinpath(exe)

        # see if it is a file
        if exe_path.exists():
            exe = exe_path
        elif shutil.which(exe) is not None:
            exe = Path(shutil.which(exe))
        else:
            logger.debug(f"Failed to find executable: {exe}")
            exe = None
        try:
            if exe and not os.access(exe, os.X_OK):
                self.update_script_mode(exe)
        except:
            logger.debug(f"Failed to change file mode for executable: {exe}")

    def create_batch_file(self, item: Union[Experiment, Simulation], **kwargs) -> None:
        """
        Create batch file.
        Args:
            item: the item to build batch file for
            kwargs: keyword arguments used to expand functionality.
        Returns:
            None
        """
        if isinstance(item, Experiment):
            max_running_jobs = kwargs.get('max_running_jobs', None)
            generate_script(self.platform, item, max_running_jobs)
        elif isinstance(item, Simulation):
            retries = kwargs.get('retries', None)
            generate_simulation_script(self.platform, item, retries)
        else:
            raise NotImplementedError(f"{item.__class__.__name__} is not supported for batch creation.")

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
            result = subprocess.run(['sbatch', '--parsable', 'sbatch.sh'], stdout=subprocess.PIPE,
                                    cwd=str(working_directory))
            slurm_job_id = result.stdout.decode('utf-8').strip().split(';')[0]
            return slurm_job_id
        elif isinstance(item, Simulation):
            pass
        else:
            raise NotImplementedError(f"Submit job is not implemented on SlurmPlatform.")

    def get_simulation_status(self, sim_id: str, **kwargs) -> EntityStatus:
        """
        Retrieve simulation status.
        Args:
            sim_id: Simulation ID
            kwargs: keyword arguments used to expand functionality
        Returns:
            EntityStatus
        """
        # Workaround (cancelling job not output -1): check if slurm job finished
        sim_dir = self.get_directory_by_id(sim_id, ItemType.SIMULATION)

        # Check process status
        job_status_path = sim_dir.joinpath('job_status.txt')
        if job_status_path.exists():
            status = open(job_status_path).read().strip()
            if status in ['100', '0', '-1']:
                status = SLURM_MAPS[status]
            else:
                status = SLURM_MAPS['100']  # To be safe
        else:
            status = SLURM_MAPS['None']

        return status

    def create_file(self, file_path: str, content: str) -> None:
        """
        Create a file with given content and file path.

        Args:
            file_path: the full path of the file to be created
            content: file content
        Returns:
            Nothing
        """
        with open(file_path, 'w') as f:
            f.write(content)

    # region: Cancel Slurm Job
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

    def get_job_id(self, item_id: str, item_type: ItemType) -> str:
        """
        Retrieve the job id for item that had been run.
        Args:
            item_id: id of experiment/simulation
            item_type: ItemType (Experiment or Simulation)
        Returns:
            str
        """
        if item_type not in (ItemType.EXPERIMENT, ItemType.SIMULATION):
            raise RuntimeError(f"Not support item type: {item_type}")

        item_dir = self.get_directory_by_id(item_id, item_type)
        job_id_file = item_dir.joinpath('job_id.txt')
        if not job_id_file.exists():
            logger.debug(f"{job_id_file} not found.")
            return None

        job_id = open(job_id_file).read().strip()
        return job_id

    # endregion
