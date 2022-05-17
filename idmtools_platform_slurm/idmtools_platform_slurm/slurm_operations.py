"""
Here we implement the SlurmPlatform operations.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import os
import copy
import dataclasses
from enum import Enum
from pathlib import Path
from datetime import datetime
from logging import getLogger
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Union, Type, Any
from paramiko import SSHClient, SFTP, AutoAddPolicy
from idmtools.core import EntityStatus
from idmtools.core.interfaces.ientity import IEntity
from idmtools.entities import Suite
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation

SIMULATION_SH_FILE = '_run.sh'
EXPERIMENT_SH_FILE = 'job_submit.sh'

logger = getLogger(__name__)


def asdict(obj, *, dict_factory=dict):
    """Return the fields of a dataclass instance as a new dictionary mapping
    field names to field values.

    Example usage:

      @dataclass
      class C:
          x: int
          y: int

      c = C(1, 2)
      assert asdict(c) == {'x': 1, 'y': 2}

    If given, 'dict_factory' will be used instead of built-in dict.
    The function applies recursively to field values that are
    dataclass instances. This will also look into built-in containers:
    tuples, lists, and dicts.
    """
    if not dataclasses.is_dataclass(obj):
        raise TypeError("asdict() should be called on dataclass instances")
    return _asdict_inner(obj, dict_factory)


def _asdict_inner(obj, dict_factory):
    if dataclasses.is_dataclass(obj):
        result = []
        for f in dataclasses.fields(obj):
            if 'pickle_function' in f.metadata:
                value = _asdict_inner(f.metadata['pickle_function'](getattr(obj, f.name)), dict_factory)
            elif 'pickle_ignore' in f.metadata and f.metadata['pickle_ignore']:
                pass
            else:
                value = _asdict_inner(getattr(obj, f.name), dict_factory)
            result.append((f.name, value))
        return dict_factory(result)
    elif isinstance(obj, tuple) and hasattr(obj, '_fields'):
        # obj is a namedtuple.  Recurse into it, but the returned
        # object is another namedtuple of the same type.  This is
        # similar to how other list- or tuple-derived classes are
        # treated (see below), but we just need to create them
        # differently because a namedtuple's __init__ needs to be
        # called differently (see bpo-34363).

        # I'm not using namedtuple's _asdict()
        # method, because:
        # - it does not recurse in to the namedtuple fields and
        #   convert them to dicts (using dict_factory).
        # - I don't actually want to return a dict here.  The the main
        #   use case here is json.dumps, and it handles converting
        #   namedtuples to lists.  Admittedly we're losing some
        #   information here when we produce a json list instead of a
        #   dict.  Note that if we returned dicts here instead of
        #   namedtuples, we could no longer call asdict() on a data
        #   structure where a namedtuple was used as a dict key.

        return type(obj)(*[_asdict_inner(v, dict_factory) for v in obj])
    elif isinstance(obj, (list, tuple)):
        # Assume we can create an object of this type by passing in a
        # generator (which is not true for namedtuples, handled
        # above).
        return type(obj)(_asdict_inner(v, dict_factory) for v in obj)
    elif isinstance(obj, dict):
        return type(obj)((_asdict_inner(k, dict_factory),
                          _asdict_inner(v, dict_factory))
                         for k, v in obj.items())
    else:
        return copy.deepcopy(obj)


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

DEFAULT_SIMULATION_BATCH = """#!/bin/bash
# Create by idm-tools at {now} in {mode}
#SBATCH --job-name={simulation.uid}
#SBATCH --output={outputfile}
"""


class SlurmOperationalMode(Enum):
    SSH = 'ssh'
    LOCAL = 'local'


@dataclass
class SlurmOperations(ABC):
    platform: 'SlurmPlatform'  # noqa: F821
    platform_type: Type = field(default=None)

    @abstractmethod
    def mk_directory(self, item: IEntity) -> None:
        pass

    @abstractmethod
    def link_dir(self, target: Union[Path, str], link: Union[Path, str]) -> None:
        pass

    @abstractmethod
    def get_batch_content(self, item: IEntity, **kwargs) -> str:
        pass

    @abstractmethod
    def create_batch_file(self, item: IEntity, **kwargs) -> None:
        pass

    @abstractmethod
    def submit_job(self, sjob_file_path: Union[Path, str]) -> None:
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

    def mk_directory(self, item: IEntity) -> None:
        pass

    def link_dir(self, target: Union[Path, str], link: Union[Path, str]) -> None:
        pass

    def get_batch_content(self, item: IEntity, **kwargs) -> str:
        pass

    def create_batch_file(self, item: IEntity, **kwargs) -> None:
        pass

    def submit_job(self, sjob_file_path: Union[Path, str]) -> None:
        pass

    def entity_status(self, item: IEntity) -> Any:
        pass


@dataclass
class LocalSlurmOperations(SlurmOperations):

    def __post_init__(self):
        pass

    def get_entity_dir(self, item: Union[Suite, Experiment, Simulation]) -> Path:
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
            suite_dir = self.get_entity_dir(suite)
            item_dir = Path(suite_dir, item.id)
        elif isinstance(item, Simulation):
            exp = item.parent
            if exp is None:
                raise RuntimeError("Simulation missing parent!")
            exp_dir = self.get_entity_dir(exp)
            item_dir = Path(exp_dir, item.id)

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
            target = self.get_entity_dir(item)
        else:
            raise RuntimeError('Only support Suite/Experiment/Simulation or not None dest.')
        os.makedirs(target, exist_ok=exist_ok)

    # @cache
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
        os.symlink(target, link)

    # @cache
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
        os.symlink(target, link)

    def get_batch_configs(self, **kwargs) -> str:
        """
        Utility: build Batch for configuration part.
        Args:
            kwargs: dynamic parameters
        Returns:
            text
        """
        contents = ''
        sbatch_configs = self.platform.get_slurm_configs(**kwargs)
        for p, v in sbatch_configs.items():
            if not v:
                continue

            p = p.replace('_', '-')
            if p == 'modules':
                for module in v:
                    contents += f'module load {module}\n'
            else:
                contents += f'#SBATCH --{p}={v}\n'

        return contents

    def get_batch_content(self, item: Union[Experiment, Simulation], **kwargs) -> str:
        """
        Get base batch content.
        TODO: this is just a 'fake' sample, not the real one. Clinton is working on the details.
        Args:
            item: the item to build batch for
            item_path: the file path
        Returns:
            None
        """
        item_path = self.get_entity_dir(item)
        contents = self.get_batch_configs(**kwargs)
        contents += "\n"
        if isinstance(item, Experiment):
            pattern = f'*/{SIMULATION_SH_FILE}'
            for filename in item_path.glob(pattern=pattern):
                contents += f"srun {filename} &"
                contents += "\n"
            contents += "\n"
            contents += "wait"
        elif isinstance(item, Simulation):
            contents += "\n"
            contents += f"srun {item.task.command.cmd}"
        return contents

    def create_batch_file(self, item: Union[Experiment, Simulation], item_path: Union[Path, str] = None,
                          **kwargs) -> None:
        """
        Create batch file.
        Args:
            item: item: the item to build batch file for
            item_path: the file path
        Returns:
            None
        """
        if item_path is None:
            item_path = self.get_entity_dir(item)
        item_path = Path(item_path)

        contents = self.get_batch_content(item, **kwargs)
        if isinstance(item, Experiment):
            sh_file = EXPERIMENT_SH_FILE
        elif isinstance(item, Simulation):
            sh_file = SIMULATION_SH_FILE

        with open(Path(item_path, sh_file), 'w') as out:
            out.write(contents)

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
