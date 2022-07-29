"""
Here we implement the SlurmPlatform experiment operations.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import subprocess
from pathlib import Path
from uuid import UUID, uuid4
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Type, Dict, Optional, Any
from idmtools.assets import Asset, AssetCollection
from idmtools.core import ItemType
from idmtools.entities import Suite
from idmtools.entities.experiment import Experiment
from idmtools.entities.iplatform_ops.iplatform_experiment_operations import IPlatformExperimentOperations
from idmtools_platform_slurm.slurm_operations import SLURM_STATES
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

    def cancel(self, experiments: List[Experiment]) -> None:
        exps_to_cancel = [exp for exp in experiments if exp.slurm_job_id is not None]
        slurm_ids = [exp.slurm_job_id for exp in exps_to_cancel]
        self.platform._op_client.cancel_jobs(ids=slurm_ids)
        for exp in exps_to_cancel:
            for sim in exp.simulations:
                sim.status = SLURM_STATES['CANCELED']

    def get_children(self, experiment: SlurmExperiment, parent: Experiment = None, raw = True, **kwargs) -> List[Any]:
        """
        Fetch slurm experiment's children.
        Args:
            experiment: Slurm experiment
            raw: True/False
            parent: the parent of the simulations
            kwargs: keyword arguments used to expand functionality
        Returns:
            List of slurm simulations
        """
        sim_list = []
        sim_meta_list = self.platform._metas.get_children(parent)
        for meta in sim_meta_list:
            slurm_sim = SlurmSimulation(meta)
            if raw:
                sim_list.append(slurm_sim)
            else:
                sim = self.platform._simulations.to_entity(slurm_sim, parent=parent)
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

        dry_run = kwargs.get('dry_run', False)
        if not dry_run:
            working_directory = self.platform._op_client.get_directory(experiment)
            result = subprocess.run(['sbatch', '--parsable', 'sbatch.sh'],
                                    stdout=subprocess.PIPE, cwd=str(working_directory))
            # we are not capturing the cluster name, which would be [1] of the following command
            slurm_job_id = result.stdout.decode('utf-8').strip().split(';')[0]

            # obtain and record the slurm job id for the experiment
            experiment.slurm_job_id = slurm_job_id
            self.platform._metas.dump(item=experiment)
        else:
            experiment.slurm_job_id = None
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
        assets_dir = Path(self.platform._op_client.get_directory_by_id(experiment.id, ItemType.EXPERIMENT), 'Assets')
        assets_list = AssetCollection.assets_from_directory(assets_dir, recursive=True)
        for a in assets_list:
            assets.add_asset(a)
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
            exp.simulations = self.get_children(slurm_exp, parent=exp, raw=False)

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
