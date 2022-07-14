"""
Here we implement the SlurmPlatform operations.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import subprocess
from enum import Enum
from pathlib import Path
from logging import getLogger
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Union, Type, Any
from paramiko import SSHClient, SFTP, AutoAddPolicy, SSHException
from idmtools.core import EntityStatus
from idmtools.core.interfaces.ientity import IEntity
from idmtools.entities import Suite
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools_platform_slurm.assets import generate_script, generate_simulation_script

logger = getLogger(__name__)

SLURM_STATES = dict(
    BOOT_FAIL=EntityStatus.FAILED,
    CANCELED=EntityStatus.FAILED,
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

DEFAULT_SIMULATION_BATCH = """#!/bin/bash
"""


class SlurmOperationException(Exception):
    pass


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
    def mk_directory(self, item: IEntity) -> None:
        pass

    @abstractmethod
    def link_dir(self, target: Union[Path, str], link: Union[Path, str]) -> None:
        pass

    @abstractmethod
    def create_batch_file(self, item: IEntity, **kwargs) -> None:
        pass

    @abstractmethod
    def submit_job(self, sjob_file_path: Union[Path, str]) -> None:
        pass

    @abstractmethod
    def cancel_jobs(self, ids):
        """
        Cancels a set of slurm job ids. Raises SlurmOperationException on failure.
        Args:
            ids: a list of slurm job ids to cancel
        Returns:
            None
        """
        pass

    @abstractmethod
    def entity_status(self, item: IEntity) -> Any:
        pass


@dataclass
class RemoteSlurmOperations(SlurmOperations):
    hostname: str = field(default=None)
    username: str = field(default=None)
    key_file: str = field(default=None)
    port: int = field(default=22)

    _cmd_client: SSHClient = field(default=None)
    _file_client: SFTP = field(default=None)

    def __post_init__(self):
        self._cmd_client = SSHClient()
        self._cmd_client.set_missing_host_key_policy(AutoAddPolicy())
        self._cmd_client.load_system_host_keys()
        self._cmd_client.connect(self.hostname, self.port, self.username, key_filename=self.key_file, compress=True)

        self._file_client = self._cmd_client.open_sftp()

    def get_directory(self, item: IEntity) -> Path:
        pass

    def mk_directory(self, item: IEntity) -> None:
        pass

    def link_dir(self, target: Union[Path, str], link: Union[Path, str]) -> None:
        pass

    def create_batch_file(self, item: IEntity, **kwargs) -> None:
        pass

    def submit_job(self, sjob_file_path: Union[Path, str]) -> None:
        pass

    def cancel_jobs(self, ids):
        if len(ids) == 0:
            return
        try:
            self._cmd_client.exec_command(f"scancel {' '.join([str(id) for id in ids])}")
        except SSHException as e:
            raise SlurmOperationException(e.args[0])

    def entity_status(self, item: IEntity) -> Any:
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
    def update_script_mode(script_path: Union[Path, str], mode=0o755) -> None:
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

    def submit_job(self, sjob_file_path: Union[Path, str], working_directory: Union[Path, str]) -> None:
        """
        Submit a Slurm job.
        Args:
            sjob_file_path: the file content
            working_directory: the file path
        Returns:
            None
        """
        raise NotImplementedError(f"Submit job is not implemented on SlurmPlatform.")

    def entity_status(self, item: Union[Suite, Experiment, Simulation]) -> Any:
        """
        Get item status.
        Args:
            item: IEntity
        Returns:
            item status
        """
        raise NotImplementedError(f"{item.__class__.__name__} is not supported on SlurmPlatform.")

    def cancel_jobs(self, ids):
        if len(ids) == 0:
            return
        try:
            subprocess.check_output(f"scancel {' '.join([str(id) for id in ids])}")
        except subprocess.CalledProcessError as e:
            raise SlurmOperationException(e.args[0])
