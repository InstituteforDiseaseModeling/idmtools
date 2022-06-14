"""
Here we implement the SlurmPlatform experiment operations.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from uuid import UUID, uuid4
from dataclasses import dataclass, field
from typing import List, Type, Dict
from idmtools.entities.experiment import Experiment
from idmtools.entities.iplatform_ops.iplatform_experiment_operations import IPlatformExperimentOperations
from idmtools_platform_slurm.platform_operations.utils import SuiteDict, ExperimentDict


@dataclass
class SlurmPlatformExperimentOperations(IPlatformExperimentOperations):
    platform: 'SlurmPlatform'  # noqa: F821
    platform_type: Type = field(default=ExperimentDict)

    def get(self, experiment_id: UUID, **kwargs) -> Dict:
        """
        Gets an experiment from the Slurm platform.
        Args:
            experiment_id: experiment id
            kwargs: keyword arguments used to expand functionality
        Returns:
            Slurm Experiment object
        """
        raise NotImplementedError("Fetching experiments has not been implemented on the Slurm Platform")

    def platform_create(self, experiment: Experiment, **kwargs) -> Dict:
        """
        Creates an experiment on Slurm Platform.
        Args:
            experiment: idmtools experiment
            kwargs: keyword arguments used to expand functionality
        Returns:
            Slurm Experiment object created
        """
        if not isinstance(experiment.uid, UUID):
            experiment.uid = uuid4()
        self.platform._op_client.mk_directory(experiment)
        self.platform._metas.dump(experiment)
        self.platform._assets.dump_assets(experiment)
        self.platform._op_client.create_batch_file(experiment, **kwargs)

        meta = self.platform._metas.get(experiment)
        return ExperimentDict(meta)

    def get_children(self, experiment: Dict, parent=None, **kwargs) -> List[Dict]:
        """
        Fetch slurm experiment's children.
        Args:
            experiment: Slurm experiment
            parent: the parent of the simulations
            kwargs: keyword arguments used to expand functionality
        Returns:
            List of slurm simulations
        """
        raise NotImplementedError("Listing assets has not been implemented on the Slurm Platform")

    def get_parent(self, experiment: ExperimentDict, **kwargs) -> SuiteDict:
        """
        Fetches the parent of an experiment.
        Args:
            experiment: Slurm experiment
            kwargs: keyword arguments used to expand functionality
        Returns:
            The Suite being the parent of this experiment.
        """
        raise NotImplementedError("Get parent has not been implemented on the Slurm Platform")

    def platform_run_item(self, experiment: Experiment, **kwargs):
        """
        Run experiment.
        Args:
            experiment: idmtools Experiment
            kwargs: keyword arguments used to expand functionality
        Returns:
            None
        """
        pass

    def send_assets(self, experiment: Experiment, **kwargs):
        """
        Copy our experiment assets.
        Replaced by self.platform._assets.dump_assets(experiment)
        Args:
            experiment: idmtools Experiment
            kwargs: keyword arguments used to expand functionality
        Returns:
            None
        """
        pass

    def refresh_status(self, experiment: Experiment, **kwargs):
        """
        Refresh status of experiment.
        Args:
            experiment: idmtools Experiment
            kwargs: keyword arguments used to expand functionality
        Returns:
            None
        """
        raise NotImplementedError("Refresh_status has not been implemented on the Slurm Platform")
