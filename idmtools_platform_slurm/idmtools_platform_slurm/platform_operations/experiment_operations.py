"""
Here we implement the SlurmPlatform experiment operations.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import copy
from uuid import UUID, uuid4
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Type, Dict, Optional
from idmtools.assets import Asset, AssetCollection
from idmtools.core import ItemType, EntityStatus
from idmtools.entities import Suite
from idmtools.entities.experiment import Experiment
from idmtools.entities.iplatform_ops.iplatform_experiment_operations import IPlatformExperimentOperations
from idmtools_platform_slurm.platform_operations.utils import ExperimentDict, SimulationDict, SuiteDict

if TYPE_CHECKING:
    from idmtools_platform_slurm.slurm_platform import SlurmPlatform


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
        metas = self.platform._metas.filter(item_type=ItemType.EXPERIMENT, property_filter={'uid': str(experiment_id)})
        if len(metas) > 0:
            return ExperimentDict(metas[0])
        else:
            raise RuntimeError(f"Not found Experiment with id '{experiment_id}'")

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
        sim_list = []
        sim_meta_list = self.platform._metas.get_children(parent)
        for meta in sim_meta_list:
            sim = self.platform._simulations.to_entity(SimulationDict(meta), parent=parent)
            sim_list.append(sim)
        return sim_list

    def get_parent(self, experiment: ExperimentDict, **kwargs) -> SuiteDict:
        """
        Fetches the parent of an experiment.
        Args:
            experiment: Slurm experiment
            kwargs: keyword arguments used to expand functionality
        Returns:
            The Suite being the parent of this experiment.
        """
        if experiment.parent:
            return experiment.parent
        elif experiment.parent_id is None:
            return None
        else:
            return self.platform._suites.get(experiment.parent_id, raw=True, **kwargs)

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
        self.platform._assets.dump_assets(experiment)

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

    def list_assets(self, experiment: Experiment, **kwargs) -> List[Asset]:
        """
        List assets for an experiment.
        Args:
            experiment: Experiment to get assets for
            kwargs:
        Returns:
            List[Asset]
        """
        ret = self.platform._assets.list_assets(experiment, **kwargs)
        return ret

    def platform_list_files(self, experiment: Experiment, **kwargs) -> List[Asset]:
        """
        List files for a platform
        Args:
            experiment: Experiment
            kwargs: keyword arguments used to expand functionality
        Returns:
            List[Asset]
        """
        assets = self.list_assets(experiment, **kwargs)
        if experiment.assets is None:
            return assets
        else:
            exp_assets = copy.deepcopy(experiment.assets.assets)
            exp_assets.extend(assets)
        return exp_assets

    def get_assets_from_slurm_experiment(self, experiment: Dict) -> AssetCollection:
        """
        Get assets for a comps experiment.

        Args:
            experiment: Experiment to get asset collection for.

        Returns:
            AssetCollection if configuration is set and configuration.asset_collection_id is set.
        """
        assets = AssetCollection()
        for a in experiment['assets']:
            asset = Asset(absolute_path=a["absolute_path"], filename=a["filename"], relative_path=a["relative_path"])
            assets.add_asset(asset)
        return assets

    def to_entity(self, slurm_exp: Dict, parent: Optional[Suite] = None, children: bool = True, **kwargs) -> Experiment:
        """
        Convert a sim dict object to an ISimulation.
        Args:
            slurm_exp: simulation to convert
            parent: optional experiment object
            children: bool True/False
            kwargs: keyword arguments used to expand functionality
        Returns:
            Experiment object
        """
        if parent is None:
            parent = self.platform.get_item(slurm_exp["parent_id"], ItemType.SUITE, force=True)
        exp = Experiment()
        exp.platform = self.platform
        exp._uid = UUID(slurm_exp['uid'])
        exp.name = slurm_exp['name']
        exp.parent_id = parent.id
        exp.parent = parent
        exp.tags = slurm_exp['tags']
        exp._platform_object = slurm_exp
        exp.status = EntityStatus[slurm_exp['status']] if slurm_exp['status'] else EntityStatus.CREATED

        exp.assets = self.get_assets_from_slurm_experiment(slurm_exp)
        if exp.assets is None:
            exp.assets = AssetCollection()

        if children:
            exp.simulations = self.get_children(slurm_exp, parent=exp)

        return exp

    def post_run_item(self, experiment: Experiment, **kwargs) -> None:
        """
        Trigger right after commissioning experiment on platform.
        Args:
            experiment: Experiment just commissioned
            kwargs: keyword arguments used to expand functionality
        Returns:
            None
        """
        self.platform._metas.dump(experiment)
        experiment.post_run(self.platform)
