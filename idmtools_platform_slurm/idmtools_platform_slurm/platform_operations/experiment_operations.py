"""
Here we implement the SlurmPlatform experiment operations.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import os
import shutil
from pathlib import Path
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Type, Dict, Optional, Any
from idmtools.assets import Asset, AssetCollection
from idmtools.core import EntityStatus
from idmtools.core import ItemType
from idmtools.entities import Suite
from idmtools.entities.experiment import Experiment
from idmtools.entities.iplatform_ops.iplatform_experiment_operations import IPlatformExperimentOperations
from idmtools_platform_slurm.platform_operations.utils import SlurmExperiment, SlurmSimulation, SlurmSuite, \
    add_dummy_suite
from logging import getLogger

logger = getLogger(__name__)
user_logger = getLogger('user')

if TYPE_CHECKING:
    from idmtools_platform_slurm.slurm_platform import SlurmPlatform


@dataclass
class SlurmPlatformExperimentOperations(IPlatformExperimentOperations):
    platform: 'SlurmPlatform'  # noqa: F821
    platform_type: Type = field(default=SlurmExperiment)

    def get(self, experiment_id: str, **kwargs) -> Dict:
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

        # ensure experiment's parent
        experiment.parent_id = experiment.parent_id or experiment.suite_id
        if experiment.parent_id is None:
            suite = add_dummy_suite(experiment)
            self.platform._suites.platform_create(suite)
            # update parent
            experiment.parent = suite

        # Generate Suite/Experiment/Simulation folder structure
        self.platform._op_client.mk_directory(experiment, exist_ok=False)
        meta = self.platform._metas.dump(experiment)
        self.platform._assets.dump_assets(experiment)
        self.platform._op_client.create_batch_file(experiment, **kwargs)

        # Copy file run_simulation.sh
        run_simulation_script = Path(__file__).parent.parent.joinpath('assets/run_simulation.sh')
        dest_script = Path(self.platform._op_client.get_directory(experiment)).joinpath('run_simulation.sh')
        shutil.copy(str(run_simulation_script), str(dest_script))

        # Make executable
        self.platform._op_client.update_script_mode(dest_script)

        # Return Slurm Experiment
        return SlurmExperiment(meta)

    def get_children(self, experiment: SlurmExperiment, parent: Experiment = None, raw=True, **kwargs) -> List[Any]:
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
        sim_meta_list = self.platform._metas.get_children(experiment)
        for meta in sim_meta_list:
            slurm_sim = SlurmSimulation(meta)
            slurm_sim.status = self.platform._op_client.get_simulation_status(slurm_sim.id)
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

    def platform_run_item(self, experiment: Experiment, dry_run: bool = False, **kwargs):
        """
        Run experiment.
        Args:
            experiment: idmtools Experiment
            dry_run: True/False
            kwargs: keyword arguments used to expand functionality
        Returns:
            None
        """
        # Ensure parent
        experiment.parent.add_experiment(experiment)
        self.platform._metas.dump(experiment.parent)
        # Generate/update metadata
        self.platform._metas.dump(experiment)
        # Commission
        if not dry_run:
            self.platform._op_client.submit_job(experiment, **kwargs)

        suite_id = experiment.parent_id or experiment.suite_id

        # user_logger.info(f'job_id: {slurm_job_id}')
        user_logger.info(f'job_directory: {Path(self.platform.job_directory).resolve()}')
        user_logger.info(f'suite: {str(suite_id)}')
        user_logger.info(f'experiment: {experiment.id}')
        user_logger.info(f"\nExperiment Directory: \n{self.platform.get_directory(experiment)}")

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
        if assets_dir.exists():
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
        exp.uid = slurm_exp.uid
        exp.name = slurm_exp.name
        exp.parent_id = parent.id
        exp.parent = parent
        exp.tags = slurm_exp.tags
        exp._platform_object = slurm_exp
        exp.simulations = []

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
            Dict of simulation id as key and working dir as value
        """
        # Check if file job_id.txt exists
        job_id_path = self.platform._op_client.get_directory(experiment).joinpath('job_id.txt')
        if not job_id_path.exists():
            logger.debug(f'job_id is not available for experiment: {experiment.id}')
            return

        # Refresh status for each simulation
        for sim in experiment.simulations:
            sim.status = self.platform._op_client.get_simulation_status(sim.id, **kwargs)

    def create_sim_directory_map(self, experiment_id: str) -> Dict:
        """
        Build simulation working directory mapping.
        Args:
            experiment_id: experiment id

        Returns:
            Dict of simulation id as key and working dir as value
        """
        exp = self.platform.get_item(experiment_id, ItemType.EXPERIMENT, raw=False)
        sims = exp.simulations
        return {sim.id: str(self.platform._op_client.get_directory(sim)) for sim in sims}

    def platform_delete(self, experiment_id: str) -> None:
        """
        Delete platform experiment.
        Args:
            experiment_id: platform experiment id
        Returns:
            None
        """
        exp = self.platform.get_item(experiment_id, ItemType.EXPERIMENT, raw=False)
        try:
            shutil.rmtree(self.platform._op_client.get_directory(exp))
        except RuntimeError:
            logger.info("Could not delete the associated experiment...")
            return

    def platform_cancel(self, experiment_id: str, force: bool = True) -> None:
        """
        Cancel platform experiment's slurm job.
        Args:
            experiment_id: experiment id
            force: bool, True/False
        Returns:
            Any
        """
        experiment = self.platform.get_item(experiment_id, ItemType.EXPERIMENT, raw=False)
        if force or experiment.status == EntityStatus.RUNNING:
            logger.debug(f"cancel slurm job for experiment: {experiment_id}...")
            job_id = self.platform._op_client.get_job_id(experiment_id, ItemType.EXPERIMENT)
            if job_id is None:
                logger.debug(f"Slurm job for experiment: {experiment_id} is not available!")
            else:
                result = self.platform._op_client.cancel_job(job_id)
                user_logger.info(f"Cancel Experiment {experiment_id}: {result}")
        else:
            user_logger.info(f"Experiment {experiment_id} is not running, no cancel needed...")

    def post_run_item(self, experiment: Experiment, **kwargs):
        """
        Trigger right after commissioning experiment on platform.

        Args:
            experiment: Experiment just commissioned
            kwargs: keyword arguments used to expand functionality
        Returns:
            None
        """
        super().post_run_item(experiment, **kwargs)

        job_ids = self.platform._op_client.get_job_id(experiment.id, ItemType.EXPERIMENT)
        if job_ids is None:
            logger.debug(f"Slurm job for experiment: {experiment.id} is not available!")
            user_logger.info("Slurm Job Ids: None")
        else:
            job_ids = [f'{" ".ljust(3)}{id}' for id in job_ids]
            user_logger.info(f"Slurm Job Ids ({len(job_ids)}):")
            user_logger.info('\n'.join(job_ids))

        user_logger.info(
            f'\nYou may try the following command to check simulations running status: \n  idmtools slurm {os.path.abspath(self.platform.job_directory)} status --exp-id {experiment.id}')
