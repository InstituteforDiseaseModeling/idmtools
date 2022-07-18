"""
Here we implement the SlurmPlatform experiment operations.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import copy
from pathlib import Path
from uuid import UUID, uuid4
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Type, Dict, Optional
from idmtools.assets import Asset, AssetCollection
from idmtools.core import ItemType
from idmtools.entities import Suite
from idmtools.entities.experiment import Experiment
from idmtools.entities.iplatform_ops.iplatform_experiment_operations import IPlatformExperimentOperations
from idmtools_platform_slurm.platform_operations.utils import SlurmExperiment, SlurmSimulation, SlurmSuite

if TYPE_CHECKING:
    from idmtools_platform_slurm.slurm_platform import SlurmPlatform


@dataclass
class SlurmPlatformExperimentOperations(IPlatformExperimentOperations):
    platform: 'SlurmPlatform'  # noqa: F821
    platform_type: Type = field(default=SlurmExperiment)

    def get(self, experiment_id: UUID, **kwargs) -> Dict:
        """
        Gets an experiment from the Slurm platform.
        Args:
            experiment_id: experiment id
            kwargs: keyword arguments used to expand functionality
        Returns:
            Slurm Experiment object
        """
        metas = self.platform._metas.filter(item_type=ItemType.EXPERIMENT, property_filter={'id': str(experiment_id)})
        if len(metas) > 0:
            return SlurmExperiment(metas[0])
        else:
            raise RuntimeError(f"Not found Experiment with id '{experiment_id}'")

    def platform_create(self, experiment: Experiment, **kwargs) -> SlurmExperiment:
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
        # Generate Suite/Experiment/Simulation folder structure
        self.platform._op_client.mk_directory(experiment)
        self.platform._assets.dump_assets(experiment)
        self.platform._op_client.create_batch_file(experiment, **kwargs)

        # Link file run_simulation.sh
        run_simulation_script = Path(__file__).parent.parent.joinpath('assets/run_simulation.sh')
        link_script = Path(self.platform._op_client.get_directory(experiment)).joinpath('run_simulation.sh')
        self.platform._op_client.link_file(run_simulation_script, link_script)
        self.platform._op_client.update_script_mode(link_script)

        # Make executable
        self.platform._op_client.update_script_mode(link_script)

        # Return Slurm Experiment
        meta = self.platform._metas.get(experiment)
        return SlurmExperiment(meta)

    def get_children(self, experiment: SlurmExperiment, parent: Experiment = None, **kwargs) -> List[SlurmSimulation]:
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
            sim = self.platform._simulations.to_entity(SlurmSimulation(meta), parent=parent)
            sim_list.append(sim)
        return sim_list

    def get_parent(self, experiment: SlurmExperiment, **kwargs) -> SlurmSuite:
        """
        Fetches the parent of an experiment.
        Args:
            experiment: Slurm experiment
            kwargs: keyword arguments used to expand functionality
        Returns:
            The Suite being the parent of this experiment.
        """
        if experiment.parent_id is None:
            return None
        else:
            return self.platform._suites.get(experiment.parent_id, raw=True, **kwargs)

    def platform_run_item(self, experiment: Experiment, **kwargs):
        """
        Run experiment.
        Args:
            experiment: idmtools Experiment
            kwargs: keyword arguments used to expand functionality
        Returns:
            None
        """
        self.platform._metas.dump(experiment)
        stdout = self.platform._op_client.submit_job(experiment, **kwargs)
        print(stdout)

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

    def list_assets(self, experiment: Experiment, **kwargs) -> List[Asset]:
        """
        List assets for an experiment.
        Args:
            experiment: Experiment to get assets for
            kwargs:
        Returns:
            List[Asset]
        """
        assets = self.platform._assets.list_assets(experiment, **kwargs)
        return assets

    def get_assets_from_slurm_experiment(self, experiment: SlurmExperiment) -> AssetCollection:
        """
        Get assets for a comps experiment.
        Args:
            experiment: Experiment to get asset collection for.
        Returns:
            AssetCollection if configuration is set and configuration.asset_collection_id is set.
        """
        assets = AssetCollection()
        for a in experiment.assets:
            if a["absolute_path"] == a["filename"]:
                abs_path = self.platform._op_client.get_directory_by_id(experiment.id, item_type=ItemType.EXPERIMENT).joinpath(f'Assets/{a["filename"]}')
                asset = Asset(absolute_path=abs_path, filename=a["filename"], relative_path=a["relative_path"])
            else:
                asset = Asset(absolute_path=a["absolute_path"], filename=a["filename"], relative_path=a["relative_path"])
            assets.add_asset(asset)
        return assets

    def to_entity(self, slurm_exp: SlurmExperiment, parent: Optional[Suite] = None, children: bool = True,
                  **kwargs) -> Experiment:
        """
        Convert a SlurmExperiment  to idmtools Experiment.
        Args:
            slurm_exp: simulation to convert
            parent: optional experiment object
            children: bool
            kwargs:
        Returns:
            Experiment object
        """
        if parent is None:
            parent = self.platform.get_item(slurm_exp.parent_id, ItemType.SUITE, force=True)
        exp = Experiment()
        exp.platform = self.platform
        exp.uid = UUID(slurm_exp.uid)
        exp.name = slurm_exp.name
        exp.parent_id = parent.id
        exp.parent = parent
        exp.tags = slurm_exp.tags
        exp._platform_object = slurm_exp

        exp.assets = self.get_assets_from_slurm_experiment(slurm_exp)
        if exp.assets is None:
            exp.assets = AssetCollection()

        if children:
            exp.simulations = self.get_children(slurm_exp, parent=exp)

        return exp

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
