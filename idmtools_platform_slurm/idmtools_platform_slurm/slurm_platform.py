import os
from collections import defaultdict
from dataclasses import dataclass, field
from logging import getLogger
from typing import Optional
from uuid import uuid4
from idmtools.entities import IPlatform
from idmtools.entities.iexperiment import TExperiment
from idmtools.entities.isimulation import TSimulation
from idmtools_platform_slurm.slurm_operations import SlurmOperationalMode, SlurmOperations, \
    RemoteSlurmOperations, LocalSlurmOperations, SLURM_STATES

logger = getLogger(__name__)


@dataclass
class SlurmPlatform(IPlatform):
    job_directory: str = None
    mode: SlurmOperationalMode = None
    mail_type: Optional[str] = None
    mail_user: Optional[str] = None

    # options for ssh mode
    remote_host: Optional[str] = None
    remote_port: int = 22
    remote_user: Optional[str] = None
    key_file: Optional[str] = None

    _op_client: SlurmOperations = field(default=None, metadata={"pickle_ignore": True})

    def __post_init__(self):
        super().__post_init__()
        if self.job_directory is None:
            raise ValueError("Job Directory is required")

        self.mode = SlurmOperationalMode[self.mode.upper()]
        if self.mode == SlurmOperationalMode.SSH:
            if self.remote_host is None or self.remote_user is None:
                raise ValueError("remote_host, remote_user and key_file are required configuration parameters "
                                 "when the mode is SSH")
            self._op_client = RemoteSlurmOperations(self.remote_host, self.remote_user, self.key_file,
                                                    port=self.remote_port)
        else:
            self._op_client = LocalSlurmOperations()

    def create_experiment(self, experiment: TExperiment) -> None:
        experiment.uid = str(uuid4())
        exp_dir = os.path.join(self.job_directory, experiment.uid)
        self._op_client.mk_directory(exp_dir)
        # store job info in the directory
        self._op_client.dump_metadata(experiment, os.path.join(exp_dir, 'experiment.json'))
        self.send_assets_for_experiment(experiment)

    def create_simulations(self, simulations_batch: 'TSimulationBatch') -> 'List[Any]':
        ids = []

        common_asset_dir = os.path.join(self.job_directory, simulations_batch[0].experiment.uid, 'Assets')

        for simulation in simulations_batch:
            simulation.uid = str(uuid4())
            sim_dir = os.path.join(self.job_directory, simulation.experiment.uid, simulation.uid)
            self._op_client.mk_directory(sim_dir)
            # store sim info in folder
            self._op_client.dump_metadata(simulation, os.path.join(sim_dir, 'simulation.json'))
            self._op_client.link_dir(common_asset_dir, os.path.join(sim_dir, 'Assets'))
            self.send_assets_for_simulation(simulation)
            ids.append(simulation.uid)
            self._op_client.create_simulation_batch_file(simulation, sim_dir, mail_type=self.mail_type,
                                                         mail_user=self.mail_user)
        return ids

    def run_simulations(self, experiment: 'TExperiment') -> None:
        for simulation in experiment.simulations:
            sim_dir = os.path.join(self.job_directory, simulation.experiment.uid, simulation.uid)
            self._op_client.submit_job(os.path.join(sim_dir, 'submit-simulation.sh'), sim_dir)

    def send_assets_for_experiment(self, experiment: 'TExperiment', **kwargs) -> None:
        for asset in experiment.assets:
            exp_asset_dir = os.path.join(self.job_directory, experiment.uid, 'Assets')
            self._op_client.mk_directory(exp_asset_dir)
            self._op_client.copy_asset(asset, exp_asset_dir)

    def send_assets_for_simulation(self, simulation: 'TSimulation', **kwargs) -> None:
        # Go through all the assets
        for asset in simulation.assets:
            sim_dir = os.path.join(self.job_directory, simulation.experiment.uid, simulation.uid)
            self._op_client.copy_asset(asset, sim_dir)

    def refresh_experiment_status(self, experiment: 'TExperiment') -> None:
        states = defaultdict(int)
        sim_states = self._op_client.experiment_status(experiment)
        for s in experiment.simulations:
            if s.uid in sim_states:
                s.status = SLURM_STATES[sim_states[s.uid]]
            states[s.status] += 1

        return experiment

    def restore_simulations(self, experiment: 'TExperiment') -> None:
        pass

    def get_assets_for_simulation(self, simulation: 'TSimulation', output_files: 'List[str]') -> 'Dict[str, bytearray]':
        pass

    def retrieve_experiment(self, experiment_id: 'uuid') -> 'TExperiment':
        pass

