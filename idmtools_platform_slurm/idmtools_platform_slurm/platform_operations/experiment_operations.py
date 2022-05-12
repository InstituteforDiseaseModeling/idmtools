import os
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Any, Tuple, Type
from uuid import UUID, uuid4

from idmtools.assets import Asset
from idmtools.entities.experiment import Experiment
from idmtools.entities.iplatform_ops.iplatform_experiment_operations import IPlatformExperimentOperations
from idmtools_platform_slurm.slurm_operations import SLURM_STATES


@dataclass
class SlurmPlatformExperimentOperations(IPlatformExperimentOperations):

    platform: 'SlurmPlatform'  # noqa: F821
    platform_type: Type = Experiment

    def get(self, experiment_id: UUID, **kwargs) -> Any:
        """
        Gets an experiment from the slurm platform.

        Args:
            experiment_id: Id to fetch
            **kwargs:

        Returns:
            Experiment object
        """
        raise NotImplementedError("Fetching experiments has not been implemented on the Slurm Platform")

    def platform_create(self, experiment: Experiment, **kwargs) -> Tuple[Experiment, UUID]:
        """
        Creates an experiment on a platform.

        Args:
            experiment: Experiment to creat
            **kwargs: Any extra args

        Returns:
            Experiment and id created.
        """
        experiment.uid = str(uuid4())
        exp_dir = os.path.join(self.platform.job_directory, experiment.uid)
        self.platform._op_client.mk_directory(exp_dir)
        # store job info in the directory
        self.platform._op_client.dump_metadata(experiment, os.path.join(exp_dir, 'experiment.json'))
        self.send_assets(experiment)
        return experiment, experiment.uid

    def get_children(self, experiment: Any, **kwargs) -> List[Any]:
        """
        Fetch children.

        TODO: Use metadata to load this + statusing?
        Args:
            experiment:
            **kwargs:

        Returns:

        """
        raise NotImplementedError("Listing assets has not been implemented on the Slurm Platform")

    def get_parent(self, experiment: Any, **kwargs) -> Any:
        """
        Get parent(suites).

        TODO: Implement Suites then this
        Args:
            experiment: Experiment to get parent for
            **kwargs:

        Returns:
            Parent if found
        """
        return None

    def platform_run_item(self, experiment: Experiment, **kwargs):
        """
        Run experiment

        TODO: Write a master sbatch script that leverages list of scripts to call

        Args:
            experiment:
            **kwargs:

        Returns:

        """
        raise NotImplementedError("TODO")

    def send_assets(self, experiment: Experiment, **kwargs):
        """
        Copy our experiment assets

        TODO: Move logic to AssetOperations
        Args:
            experiment:
            **kwargs:

        Returns:
            None
        """
        for asset in experiment.assets:
            exp_asset_dir = os.path.join(self.platform.job_directory, experiment.uid, 'Assets')
            self.platform._op_client.mk_directory(exp_asset_dir)
            self.platform._op_client.copy_asset(asset, exp_asset_dir)

    def refresh_status(self, experiment: Experiment, **kwargs):
        """
        Refresh status of experiment.

        TODO: Leverage the filesystem/metadata for this vs slurm
        Args:
            experiment: Experiment
            **kwargs:

        Returns:
            None
        """
        states = defaultdict(int)
        sim_states = self.platform._op_client.experiment_status(experiment)
        for s in experiment.simulations:
            if s.uid in sim_states:
                s.status = SLURM_STATES[sim_states[s.uid]]
            states[s.status] += 1

    def list_assets(self, experiment: Experiment, **kwargs) -> List[str]:
        """
        List assets for an experiment.

        TODO: DO this later

        Args:
            experiment: Experiment to get assets for
            **kwargs:

        Returns:

        """
        raise NotImplementedError("Listing assets has not been implemented on the Slurm Platform")

    def platform_list_files(self, experiment: Experiment, **kwargs) -> List[Asset]:
        """
        List files for a platform

        Args:
            experiment: Experiment
            **kwargs:

        Returns:

        """
        raise NotImplementedError("Listing files has not been implemented on the Slurm Platform")
