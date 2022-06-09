"""
Here we implement the SlurmPlatform experiment operations.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import copy
from pathlib import Path
from uuid import UUID, uuid4
from dataclasses import dataclass, field
from typing import List, Any, Type, Dict, Optional
from idmtools.assets import Asset, AssetCollection
from idmtools.core import ItemType, EntityStatus
from idmtools.entities import Suite
from idmtools.entities.experiment import Experiment
from idmtools.entities.iplatform_ops.iplatform_experiment_operations import IPlatformExperimentOperations
from idmtools_platform_slurm.platform_operations.utils import ExperimentDict, SimulationDict


@dataclass
class SlurmPlatformExperimentOperations(IPlatformExperimentOperations):
    platform: 'SlurmPlatform'  # noqa: F821
    platform_type: Type = field(default=ExperimentDict)

    def get(self, experiment_id: UUID, **kwargs) -> Dict:
        """
        Gets an experiment from the slurm platform.
        Args:
            experiment_id: Id to fetch
            kwargs: keyword arguments used to expand functionality
        Returns:
            Experiment object
        """
        raise NotImplementedError("Fetching experiments has not been implemented on the Slurm Platform")

    def platform_create(self, experiment: Experiment, **kwargs) -> Dict:
        """
        Creates an experiment on Slurm Platform.
        Args:
            experiment: Experiment to creat
            kwargs: keyword arguments used to expand functionality
        Returns:
            Experiment created.
        """
        if not isinstance(experiment.uid, UUID):
            experiment.uid = uuid4()
        self.platform._op_client.mk_directory(experiment)
        self.platform._metas.dump(experiment)
        self.platform._assets.dump_assets(experiment)
        self.platform._op_client.create_batch_file(experiment)

        meta = self.platform._metas.get(experiment)
        return ExperimentDict(meta)

    def get_children(self, slurm_experiment: Dict, parent=None, **kwargs) -> List[Any]:
        """
        Fetch children.
        Args:
            slurm_experiment:
            parent:
            kwargs: keyword arguments used to expand functionality
        Returns:
            List[Any]
        """
        raise NotImplementedError("Listing assets has not been implemented on the Slurm Platform")

    def get_parent(self, experiment: Experiment, **kwargs) -> Any:
        """
        Fetches the parent of a experiment.
        Args:
            experiment: Experiment to get parent for
            kwargs: keyword arguments used to expand functionality
        Returns:
            The Suite being the parent of this experiment.
        """
        raise NotImplementedError("Get parent has not been implemented on the Slurm Platform")

    def platform_run_item(self, experiment: Experiment, **kwargs):
        """
        Run experiment.
        TODO: Write a master sbatch script that leverages list of scripts to call
        Args:
            experiment:
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
            experiment:
            kwargs: keyword arguments used to expand functionality
        Returns:
            None
        """
        pass

    def refresh_status(self, experiment: Experiment, **kwargs):
        """
        Refresh status of experiment.
        Args:
            experiment: Experiment
            kwargs: keyword arguments used to expand functionality
        Returns:
            None
        """
        raise NotImplementedError("Refresh_status has not been implemented on the Slurm Platform")
