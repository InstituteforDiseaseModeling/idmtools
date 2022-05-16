import copy
import dataclasses
import json
import os
import shutil
import subprocess
import tempfile
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, is_dataclass
from datetime import datetime
from enum import Enum
from io import BytesIO, StringIO
from logging import getLogger
from typing import Union, Type
from idmtools.assets import Asset
from paramiko import SSHClient, SFTP, AutoAddPolicy
from idmtools.core import EntityStatus

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
    if not is_dataclass(obj):
        raise TypeError("asdict() should be called on dataclass instances")
    return _asdict_inner(obj, dict_factory)


def _asdict_inner(obj, dict_factory):
    if is_dataclass(obj):
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
    platform_type: Type = dataclasses.field(default=None)

    @abstractmethod
    def copy_asset(self, asset, dest):
        pass

    @abstractmethod
    def download_asset(self, dest, output: Union[str, BytesIO] = None):
        pass

    @abstractmethod
    def mk_directory(self, dest):
        pass

    @abstractmethod
    def link_dir(self, src, dest):
        pass

    @abstractmethod
    def submit_job(self, job_file_path, working_directory):
        pass

    @abstractmethod
    def dump_metadata(self, object, dest):
        pass

    def get_batch_contents(self, simulation, sim_path, mail_type=None, mail_user=None, ntasks=None, qos=None,
                           time=None, nodes=None, ntasks_per_node=None, constraint=None, gres=None, mem=None,
                           exclusive=None, access=None, partition=None, mem_per_cpu=None, nodelist=None, exclude=None,
                           requeue=None, modules=None, mode='SSH'):
        """
        See https://ubccr.freshdesk.com/support/solutions/articles/5000688140-submitting-a-slurm-job-script
        Args:
            simulation:
            sim_path:
            mail_type:
            mail_user:
            ntasks:stdout_.channel.recv_exit_status()
            qos:
            time:
            nodes:
            ntasks_per_node:
            constraint:
            gres:
            mem:
            exclusive:
            access:
            partition:
            mem_per_cpu:
            nodelist:
            exclude:
            requeue:
            modules:
            mode:


        Returns:

        """
        contents = DEFAULT_SIMULATION_BATCH.format(**dict(simulation=simulation, self=self, now=str(datetime.now()),
                                                          mode=mode, outputfile=os.path.join(sim_path, 'StdOut.txt')))
        # contents += "#SBATCH --mail-type=ALL\n"
        # contents += "#SBATCH --mail-user=$USER@idmod.org\n"
        for opt in ['ntasks', 'qos', 'time', 'nodes', 'ntasks_per_node', 'constraint', 'gres', 'mem', 'account',
                    'partition', 'mem_per_cpu', 'mail_type', 'mail_user', 'exclude']:
            if opt in locals() and locals()[opt]:
                contents += f'SBATCH --{opt.replace("_", "-")}=' + locals()[opt] + "\n"
        if access:
            contents += 'SBATCH --exclusive\n'

        if requeue:
            contents += 'SBATCH --requeue\n'

        if nodelist:
            contents += f'#SBATCH -w, --nodelist={nodelist}\n'

        if modules:
            for module in modules:
                contents += f'module load {module}\n'

        return contents

    @abstractmethod
    def create_simulation_batch_file(self, simulation, sim_dir, mail_type=None, mail_user=None, ntasks=None, qos=None,
                                     time=None, nodes=None, ntasks_per_node=None, constraint=None, gres=None, mem=None,
                                     exclusive=None, access=None, partition=None, mem_per_cpu=None, nodelist=None,
                                     exclude=None,
                                     requeue=None, modules=None):

        pass

    @abstractmethod
    def experiment_status(self, experiment):
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

    def copy_asset(self, asset, dest):
        # TODO Check on windows if we have to convert EOLs on scripts and what not
        if asset.absolute_path:
            fn = os.path.basename(asset.absolute_path)
            self._file_client.put(asset.absolute_path, os.path.join(dest, fn))
        elif asset.content:
            # TODO check pathing on windows to slurm on linux
            self._file_client.putfo(BytesIO(asset.content), os.path.join(dest, asset.filename))

    def download_asset(self, dest, output: Union[str, BytesIO] = None):
        # TODO Support streaming these objects to avoid full memory
        if output is None:
            output = BytesIO()
        if isinstance(output, str):
            output = open(output, 'wb')
        self._file_client.getfo(dest, output)

    def link_dir(self, src, dest):
        self._cmd_client.exec_command(f'ln -s {src} {dest}')

    def mk_directory(self, dest):
        self._file_client.mkdir(dest)

    def dump_metadata(self, object, dest):
        tmp_file, tmp_file_name = tempfile.mkstemp()
        with open(tmp_file_name, 'w') as out:
            if is_dataclass(object):
                json.dump(asdict(object), out)
            else:
                json.dump(object, out)
        self._file_client.put(tmp_file_name, dest)
        os.remove(tmp_file_name)

    def create_simulation_batch_file(self, simulation, sim_dir, **kwargs):
        contents = self.get_batch_contents(simulation, sim_dir, mode='SSH', **kwargs)
        contents += "\n"
        contents += f"\nsrun {simulation.experiment.command.cmd}"

        self._file_client.putfo(StringIO(contents), os.path.join(sim_dir, 'submit-simulation.sh'))

    def submit_job(self, job_file_path, working_directory):
        stdin_, stdout_, stderr_ = self._cmd_client.exec_command(f'cd {working_directory}; sbatch {job_file_path}')
        logger.debug(f"SSH Output: {stdout_.readlines()}")
        logger.debug(stdout_.channel.recv_exit_status())
        # TODO verify result

    def experiment_status(self, experiment):
        stdin_, stdout_, stderr_ = self._cmd_client.exec_command('sacct -S1970-01-01T00:00 -n -p -oJobname,state')
        output_lines = reversed(stdout_.readlines())
        sids = [s.uid for s in experiment.simulations]
        sims = {}
        for line in output_lines:
            line = line.split('|')
            if line[0] in sids:
                sims[line[0]] = line[1]
                if len(sims) == len(sids):
                    break

        return sims


@dataclass
class LocalSlurmOperations(SlurmOperations):

    def experiment_status(self, experiment):
        raise NotImplementedError("TODO")

    def link_dir(self, src, dest):
        raise NotImplementedError("TODO")

    def dump_metadata(self, object, dest):
        if dataclasses.is_dataclass(object):
            json.dump(dataclasses.asdict(object), dest)
        else:
            json.dump(object, dest)

    def download_asset(self, dest, output: Union[str, BytesIO] = None):
        # TODO Support streaming these objects to avoid full memory
        if output is None:
            output = BytesIO()
        if isinstance(output, str):
            output = open(output, 'wb')
        with open(dest, 'rb') as out:
            output.write(out.read())

    def mk_directory(self, dest):
        os.makedirs(dest, exist_ok=True)

    def copy_asset(self, asset: Asset, dest):
        if asset.absolute_path:
            shutil.copy(asset.absolute_path, dest)
        elif asset.content:
            with open(os.path.join(dest, asset.filename), 'wb') as out:
                out.write(asset.content)

    def create_simulation_batch_file(self, simulation, sim_dir, **kwargs):
        contents = self.get_batch_contents(simulation, sim_dir, mode='Local', **kwargs)
        contents += "\n"
        contents += f"\nsrun {simulation.experiment.command.cmd}"
        with open(os.path.join(sim_dir, 'submit-simulation.sh'), 'w') as out:
            out.write(contents)

    def submit_job(self, job_file_path, working_directory):
        result = subprocess.check_output(['sbatch', job_file_path], cwd=working_directory)
        print(result)
        # TODO verify result

    def simulation_status(self, simulation):
        state = subprocess.check_output(['sacct', '-S1970-01-01T00:00', f'--name={simulation.uid}', '-n', '-ostate'])
        return SLURM_STATES[state]
