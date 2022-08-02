"""
Here we implement the SlurmPlatform operations.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import os
import shlex
import shutil
import subprocess
from enum import Enum
from pathlib import Path
from uuid import UUID, uuid4
from logging import getLogger
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Union, Type, Any, Dict
from idmtools.core import EntityStatus, ItemType
from idmtools.core.interfaces.ientity import IEntity
from idmtools.entities import Suite
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools_platform_slurm.assets import generate_script, generate_simulation_script

logger = getLogger(__name__)

SLURM_STATES = dict(
    BOOT_FAIL=EntityStatus.FAILED,
    CANCELLED=EntityStatus.FAILED,
    COMPLETED=EntityStatus.SUCCEEDED,
    DEADLINE=EntityStatus.FAILED,
    FAILED=EntityStatus.FAILED,
    OUT_OF_MEMORY=EntityStatus.FAILED,
    PENDING=EntityStatus.RUNNING,
    PREEMPTED=EntityStatus.FAILED,
    RUNNING=EntityStatus.RUNNING,
    REQUEUED=EntityStatus.RUNNING,
    RESIZING=EntityStatus.RUNNING,
    REVOKED=EntityStatus.FAILED,
    SUSPENDED=EntityStatus.FAILED,
    TIMEOUT=EntityStatus.FAILED
)

SLURM_MAPS = {
    "0": EntityStatus.SUCCEEDED,
    "-1": EntityStatus.FAILED,
    "100": EntityStatus.RUNNING,
    "None": EntityStatus.CREATED
}

DEFAULT_SIMULATION_BATCH = """#!/bin/bash
"""


class SlurmOperationalMode(Enum):
    SSH = 'ssh'
    LOCAL = 'local'


@dataclass
class SlurmOperations(ABC):
    platform: 'SlurmPlatform'  # noqa: F821
    platform_type: Type = field(default=None)

    @abstractmethod
    def get_directory(self, item: IEntity) -> Path:
        pass

    @abstractmethod
    def get_directory_by_id(self, item_id: str, item_type: ItemType) -> Path:
        pass

    @abstractmethod
    def make_command_executable(self, simulation: Simulation) -> None:
        pass

    @abstractmethod
    def mk_directory(self, item: IEntity) -> None:
        pass

    @abstractmethod
    def link_file(self, target: Union[Path, str], link: Union[Path, str]) -> None:
        pass

    @abstractmethod
    def link_dir(self, target: Union[Path, str], link: Union[Path, str]) -> None:
        pass

    @abstractmethod
    def update_script_mode(self, script_path: Union[Path, str], mode: int) -> None:
        pass

    @abstractmethod
    def make_command_executable(self, simulation: Simulation) -> None:
        pass

    @abstractmethod
    def create_batch_file(self, item: IEntity, **kwargs) -> None:
        pass

    @abstractmethod
    def submit_job(self, item: Union[Experiment, Simulation], **kwargs) -> Any:
        pass

    @abstractmethod
    def get_simulation_status(self, sim_id: Union[UUID, str]) -> Any:
        pass


@dataclass
class RemoteSlurmOperations(SlurmOperations):
    hostname: str = field(default=None)
    username: str = field(default=None)
    key_file: str = field(default=None)
    port: int = field(default=22)

    def get_directory(self, item: IEntity) -> Path:
        pass

    def get_directory_by_id(self, item_id: str, item_type: ItemType) -> Path:
        pass

    def mk_directory(self, item: IEntity) -> None:
        pass

    def link_file(self, target: Union[Path, str], link: Union[Path, str]) -> None:
        pass

    def link_dir(self, target: Union[Path, str], link: Union[Path, str]) -> None:
        pass

    def update_script_mode(self, script_path: Union[Path, str], mode: int) -> None:
        pass

    def make_command_executable(self, simulation: Simulation) -> None:
        pass

    def create_batch_file(self, item: IEntity, **kwargs) -> None:
        pass

    def submit_job(self, item: Union[Experiment, Simulation], **kwargs) -> Any:
        pass

    def get_simulation_status(self, sim_id: Union[UUID, str]) -> Any:
        pass


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
            suite = item.parent
            if suite is None:
                raise RuntimeError("Experiment missing parent!")
            suite_dir = self.get_directory(suite)
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
        dry_run = kwargs.get('dry_run', False)
        if isinstance(item, Experiment):
            if not dry_run:
                working_directory = self.get_directory(item)
                result = subprocess.run(['sbatch', 'sbatch.sh'], stdout=subprocess.PIPE, cwd=str(working_directory))
                stdout = result.stdout.decode('utf-8').strip()
                return stdout
        elif isinstance(item, Simulation):
            pass
        else:
            raise NotImplementedError(f"Submit job is not implemented on SlurmPlatform.")

    def get_simulation_status(self, sim_id: Union[UUID, str], job_cancelled: bool = None, raw: bool = False,
                              **kwargs) -> EntityStatus:
        """
        Retrieve simulation status.
        Args:
            sim_id: Simulation ID
            job_cancelled: bool
            raw: bool
                - True: keep original CREATED (not processed)
                - False: convert CREATED (not processed) to FAILED
            kwargs: keyword arguments used to expand functionality
        Returns:
            EntityStatus
        """
        # Workaround (cancelling job not output -1): check if slurm job got cancelled
        sim_dir = self.get_directory_by_id(sim_id, ItemType.SIMULATION)
        if job_cancelled is None:
            job_id_path = sim_dir.parent.joinpath('job_id.txt')
            if job_id_path.exists():
                job_id = open(job_id_path).read().strip()
                job_cancelled = self.check_cancelled(job_id)
            else:
                job_cancelled = False

        # Check process status
        job_status_path = sim_dir.joinpath('job_status.txt')
        if job_status_path.exists():
            status = open(job_status_path).read().strip()
            status = SLURM_MAPS[status]
        else:
            status = SLURM_MAPS['None']
        # Consider Cancel Case so that we may get out of the refresh loop
        if job_cancelled and not raw and status == EntityStatus.CREATED:
            status = EntityStatus.FAILED

        return status

    @staticmethod
    def check_cancelled(job_id: str, display: bool = False, **kwargs) -> Any:
        """
        Check if there is RUNNING or PENDING job.
        Args:
            job_id: Slurm job id
            kwargs: keyword arguments used to expand functionality
        Returns:
            Any
        """
        # Get slurm jobs summary
        p1 = subprocess.Popen(['sacct', '-n', '-X', '-P', '--format=state', '-j', job_id], stdout=subprocess.PIPE)
        p2 = subprocess.Popen(['sort'], stdin=p1.stdout, stdout=subprocess.PIPE)
        p1.stdout.close()
        p3 = subprocess.Popen(['uniq', '-c'], stdin=p2.stdout, stdout=subprocess.PIPE)
        p2.stdout.close()

        result = p3.communicate()[0]
        stdout = result.decode('utf-8').strip()
        if display:
            print(stdout)
        return ('PENDING' not in stdout) and ('RUNNING' not in stdout)
