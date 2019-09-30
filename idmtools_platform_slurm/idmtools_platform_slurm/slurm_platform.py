import json
import os
import shutil
from dataclasses import dataclass
from typing import Optional
from uuid import uuid4

from idmtools.entities import IPlatform
from idmtools.entities.iexperiment import TExperiment
from idmtools.entities.isimulation import TSimulation


@dataclass
class SlurmPlatform(IPlatform):
    job_directory: str
    qos: Optional[str] = None
    mail_type: Optional[str] = None
    mail_user: Optional[str] = None

    def __post_init__(self):
        super().__post_init__()

    def create_experiment(self, experiment: TExperiment) -> None:
        # TODO, in future, the user could be executing remotely, so we need to possibly do this over
        # ssh or locally. For now assume we are running from the head node
        experiment.uid = str(uuid4())
        exp_dir = os.path.join(self.job_directory, experiment.uid)
        os.makedirs(exp_dir, exist_ok=True)
        # store job info in the directory
        json.dump(os.path.join(exp_dir, 'experiment.json'), experiment)

    def create_simulations(self, simulations_batch: 'TSimulationBatch') -> 'List[Any]':
        ids = []

        for simulation in simulations_batch:
            simulation.uid = str(uuid4())
            # TODO, in future, the user could be executing remotely, so we need to possibly do this over
            # ssh or locally. For now assume we are running from the head node
            sim_dir = os.path.join(self.job_directory, simulation.experiment.uid, simulation.uid)
            os.makedirs(sim_dir, exist_ok=True)
            # store sim info in folder
            json.dump(os.path.join(sim_dir, 'simulation.json'), simulation)
            self.send_assets_for_simulation(simulation)
            ids.append(simulation.uid)
            self.create_sbatch_file(simulation)
        return ids

    def run_simulations(self, experiment: 'TExperiment') -> None:
        for simulation in experiment.simulations:
            sim_dir = os.path.join(self.job_directory, simulation.experiment.uid, simulation.uid)
            os.system(f'sbatch submit-job.sh -D {sim_dir}')

    def send_assets_for_experiment(self, experiment: 'TExperiment', **kwargs) -> None:
        for asset in experiment.assets:
            exp_asset_dir = os.path.join(self.job_directory, experiment.uid, 'Assets')
            os.makedirs(exp_asset_dir)
            if asset.absolute_path:
                shutil.copy(asset.absolute_path, exp_asset_dir)
            elif asset.content:
                with open(os.path.join(exp_asset_dir, asset.filename), 'wb') as out:
                    out.write(asset.content)

    def send_assets_for_simulation(self, simulation: 'TSimulation', **kwargs) -> None:
        # Go through all the assets
        for asset in simulation.assets:
            sim_dir = os.path.join(self.job_directory, simulation.experiment.uid, simulation.uid)
            if asset.absolute_path:
                shutil.copy(asset.absolute_path, sim_dir)
            elif asset.content:
                with open(os.path.join(sim_dir, asset.filename), 'wb') as out:
                    out.write(asset.content)

    def refresh_experiment_status(self, experiment: 'TExperiment') -> None:
        pass

    def restore_simulations(self, experiment: 'TExperiment') -> None:
        pass

    def get_assets_for_simulation(self, simulation: 'TSimulation', output_files: 'List[str]') -> 'Dict[str, bytearray]':
        pass

    def retrieve_experiment(self, experiment_id: 'uuid') -> 'TExperiment':
        pass

    def create_sbatch_file(self, simulation: TSimulation):
        sim_dir = os.path.join(self.job_directory, simulation.experiment.uid, simulation.uid)
        with open(os.path.join(sim_dir, 'submit-job.sh'), 'w') as out:
            out.write(f"""
#!/bin/bash
#
#SBATCH --job-name={simulation.uid}
#SBATCH --ntasks=1
            """)
            if self.mail_type:
                out.write("#SBATCH --mail-type=ALL")

            if self.mail_user:
                out.write("#SBATCH --mail-user=$USER@idmod.org")

            out.write(simulation.experiment.command.cmd)