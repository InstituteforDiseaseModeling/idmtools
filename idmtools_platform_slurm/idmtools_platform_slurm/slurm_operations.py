import json
import os
import shutil
import subprocess
import tempfile
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from io import BytesIO, StringIO

from idmtools.assets import Asset
from paramiko import SSHClient, SFTP, AutoAddPolicy


SLURM_STATES = dict(
    BOOT_FAIL='failed',
    CANCELLED='canceled',
    COMPLETED='completed',
    DEADLINE='failed',
    FAILED='failed',
    OUT_OF_MEMORY='failed',
    PENDING='pending',
    PREEMPTED='failed',
    RUNNING='in_progress',
    REQUEUED='pending',
    RESIZING='in_progress',
    REVOKED='failed',
    SUSPENDED='failed',
    TIMEOUT='failed'
)



DEFAULT_SIMULATION_BATCH = """
#!/bin/bash
# Create by idm-tools at {now} in {self.mode}
#SBATCH --job-name={simulation.uid}
#SBATCH --output={outputfile}
"""


class SlurmOperationalMode(Enum):
    SSH = 'ssh'
    LOCAL = 'local'


class SlurmOperations(ABC):
    @abstractmethod
    def copy_asset(self, asset, dest):
        pass

    @abstractmethod
    def mk_directory(self, dest):
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
                           requeue=None, modules=None):
        """
        See https://ubccr.freshdesk.com/support/solutions/articles/5000688140-submitting-a-slurm-job-script
        Args:
            simulation:
            sim_path:
            mail_type:
            mail_user:
            ntasks:
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


        Returns:

        """
        contents = DEFAULT_SIMULATION_BATCH.format(dict(simulation=simulation, self=self, now=str(datetime.now()),
                                                        outputfile=os.path.join(sim_path, 'StdOut.txt')))
        # contents += "#SBATCH --mail-type=ALL\n"
        # contents += "#SBATCH --mail-user=$USER@idmod.org\n"
        for opt in ['ntasks', 'qos', 'time', 'nodes', 'ntasks_per_node', 'constraint', 'gres', 'mem', 'account',
                    'partition', 'mem_per_cpu', 'mail_type', 'mail_user', 'exclude']:
            if locals()[opt]:
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
                           exclusive=None, access=None, partition=None, mem_per_cpu=None, nodelist=None, exclude=None,
                           requeue=None, modules=None):

        pass

    @abstractmethod
    def simulation_status(self, simulation):
        pass




@dataclass
class RemoteSlurmOperations(SlurmOperations):

    hostname: str
    username: str
    key_file: str
    port: int = 22

    _cmd_client: SSHClient = None
    _file_client: SFTP = None

    def __post_init__(self):
        self._cmd_client = SSHClient()
        self._cmd_client.set_missing_host_key_policy(AutoAddPolicy())
        self._cmd_client.load_system_host_keys()
        self._cmd_client.connect(self.hostname, self.port, self.username, key_filename=self.key_file, compress=True)

        self._file_client = self._cmd_client.open_sftp()

    def copy_asset(self, asset, dest):
        # TODO Check on windows if we have to convert EOLs on scripts and what not
        if asset.absolute_path:
            self._file_client.put(asset.absolute_path, dest)
        elif asset.content:
            # TODO check pathing on windows to slurm on linux
            self._file_client.putfo(BytesIO(asset.content), os.path.join(dest, asset.filename))

    def mk_directory(self, dest):
        self._file_client.mkdir(dest)

    def dump_metadata(self, object, dest):
        tmp_file, tmp_file_name = tempfile.mkstemp()
        json.dump(tmp_file, object)
        self._file_client.put(tmp_file_name, dest)
        os.remove(tmp_file_name)

    def create_simulation_batch_file(self, simulation, sim_dir, **kwargs):
        contents = self.get_batch_contents(simulation, sim_dir, **kwargs)
        contents += "\n"
        contents += "\nsrun out.write(simulation.experiment.command.cmd)"

        self._file_client.putfo(StringIO(contents), os.path.join(sim_dir, 'submit-simulation.sh'))

    def submit_job(self, job_file_path, working_directory):
        result = self._cmd_client.exec_command(f'cd {working_directory}; sbatch {job_file_path}')
        # TODO verify result

    def simulation_status(self, simulation):
        state = self._cmd_client.exec_command('fsacct -S1970-01-01T00:00 --name={simulation.uid} -n -ostate')
        return SLURM_STATES[state]


@dataclass
class LocalSlurmOperations(SlurmOperations):

    def dump_metadata(self, object, dest):
        json.dump(dest, object)

    def mk_directory(self, dest):
        os.makedirs(dest, exist_ok=True)

    def copy_asset(self, asset: Asset, dest):
        if asset.absolute_path:
            shutil.copy(asset.absolute_path, dest)
        elif asset.content:
            with open(os.path.join(dest, asset.filename), 'wb') as out:
                out.write(asset.content)

    def create_simulation_batch_file(self, simulation, sim_dir, **kwargs):
        contents = self.get_batch_contents(simulation, sim_dir, **kwargs)
        contents += "\n"
        contents += "\nsrun out.write(simulation.experiment.command.cmd)"
        with open(os.path.join(sim_dir, 'submit-simulation.sh'), 'w') as out:
            out.write(contents)

    def submit_job(self, job_file_path, working_directory):
        result = subprocess.check_output(['sbatch', job_file_path], cwd=working_directory)
        # TODO verify result

    def simulation_status(self, simulation):
        state = subprocess.check_output(['sacct', '-S1970-01-01T00:00', f'--name={simulation.uid}', '-n', '-ostate'])
        return SLURM_STATES[state]
