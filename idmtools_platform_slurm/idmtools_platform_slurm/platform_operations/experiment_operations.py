import os
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Any, Tuple, Type
from uuid import UUID, uuid4
from idmtools.entities import IExperiment
from idmtools.entities.iplatform_ops.iplatform_experiment_operations import IPlatformExperimentOperations
from idmtools_platform_slurm.slurm_operations import SLURM_STATES


@dataclass
class SlurmPLatformExperimentOperations(IPlatformExperimentOperations):
    platform: 'SlurmPlatform'
    platform_type: Type = IExperiment

    def get(self, experiment_id: UUID, **kwargs) -> Any:
        raise NotImplementedError("Fetching experiments has not been implemented on the Slurm Platform")

    def platform_create(self, experiment: IExperiment, **kwargs) -> Tuple[IExperiment, UUID]:
        experiment.uid = str(uuid4())
        exp_dir = os.path.join(self.platform.job_directory, experiment.uid)
        self.platform._op_client.mk_directory(exp_dir)
        # store job info in the directory
        self.platform._op_client.dump_metadata(experiment, os.path.join(exp_dir, 'experiment.json'))
        self.send_assets(experiment)
        return experiment, experiment.uid

    def get_children(self, experiment: Any, **kwargs) -> List[Any]:
        raise NotImplementedError("Listing assets has not been implemented on the Slurm Platform")

    def get_parent(self, experiment: Any, **kwargs) -> Any:
        return None

    def platform_run_item(self, experiment: IExperiment):
        for simulation in experiment.simulations:
            self.platform._simulations.run_item(simulation)

    def send_assets(self, experiment: IExperiment):
        for asset in experiment.assets:
            exp_asset_dir = os.path.join(self.platform.job_directory, experiment.uid, 'Assets')
            self.platform._op_client.mk_directory(exp_asset_dir)
            self.platform._op_client.copy_asset(asset, exp_asset_dir)

    def refresh_status(self, experiment: IExperiment):
        states = defaultdict(int)
        sim_states = self.platform._op_client.experiment_status(experiment)
        for s in experiment.simulations:
            if s.uid in sim_states:
                s.status = SLURM_STATES[sim_states[s.uid]]
            states[s.status] += 1

    def list_assets(self, experiment: IExperiment) -> List[str]:
        raise NotImplementedError("Listing assets has not been implemented on the Slurm Platform")
