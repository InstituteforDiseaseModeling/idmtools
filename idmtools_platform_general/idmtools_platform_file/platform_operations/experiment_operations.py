"""
Here we implement the FilePlatform experiment operations.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import shutil
from pathlib import Path
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Type, Dict, Optional, Any
from idmtools.assets import Asset, AssetCollection
from idmtools.core import ItemType
from idmtools.entities import Suite
from idmtools.entities.experiment import Experiment
from idmtools.entities.iplatform_ops.iplatform_experiment_operations import IPlatformExperimentOperations
from idmtools_platform_file.platform_operations.utils import FileExperiment, FileSimulation, FileSuite, add_dummy_suite
from logging import getLogger

logger = getLogger(__name__)
user_logger = getLogger('user')

if TYPE_CHECKING:
    from idmtools_platform_file.file_platform import FilePlatform


@dataclass
class FilePlatformExperimentOperations(IPlatformExperimentOperations):
    """
    Experiment Operations for File Platform.
    """
    platform: 'FilePlatform'  # noqa: F821
    platform_type: Type = field(default=FileExperiment)
    RUN_SIMULATION_SCRIPT_PATH = Path(__file__).parent.parent.joinpath('assets/run_simulation.sh')

    def get(self, experiment_id: str, **kwargs) -> FileExperiment:
        """
        Gets an experiment from the File platform.
        Args:
            experiment_id: experiment id
            kwargs: keyword arguments used to expand functionality
        Returns:
            File Experiment object
        """
        metas = self.platform._metas.filter(item_type=ItemType.EXPERIMENT, property_filter={'id': str(experiment_id)})
        if len(metas) > 0:
            return FileExperiment(metas[0])
        else:
            raise RuntimeError(f"Not found Experiment with id '{experiment_id}'")

    def platform_create(self, experiment: Experiment, **kwargs) -> FileExperiment:
        """
        Creates an experiment on File Platform.
        Args:
            experiment: idmtools experiment
            kwargs: keyword arguments used to expand functionality
        Returns:
            File Experiment object created
        """
        # ensure experiment's parent
        experiment.parent_id = experiment.parent_id or experiment.suite_id
        if experiment.parent_id is None:
            suite = add_dummy_suite(experiment)
            self.platform._suites.platform_create(suite)
            suite.platform = self.platform

        # Generate Suite/Experiment/Simulation folder structure
        self.platform.mk_directory(experiment, exist_ok=True)
        meta = self.platform._metas.dump(experiment)
        self.platform._assets.dump_assets(experiment)
        self.platform.create_batch_file(experiment, **kwargs)

        # Copy file run_simulation.sh
        dest_script = Path(self.platform.get_directory(experiment)).joinpath('run_simulation.sh')
        shutil.copy(str(self.RUN_SIMULATION_SCRIPT_PATH), str(dest_script))

        # Make executable
        self.platform.update_script_mode(dest_script)

        # Return File Experiment
        return FileExperiment(meta)

    def get_children(self, experiment: FileExperiment, parent: Experiment = None, raw=True, **kwargs) -> List[Any]:
        """
        Fetch file experiment's children.
        Args:
            experiment: File experiment
            raw: True/False
            parent: the parent of the simulations
            kwargs: keyword arguments used to expand functionality
        Returns:
            List of file simulations
        """
        sim_list = []
        sim_meta_list = self.platform._metas.get_children(experiment)
        for meta in sim_meta_list:
            file_sim = FileSimulation(meta)
            file_sim.status = self.platform.get_simulation_status(file_sim.id)
            if raw:
                sim_list.append(file_sim)
            else:
                sim = self.platform._simulations.to_entity(file_sim, parent=parent)
                sim_list.append(sim)
        return sim_list

    def get_parent(self, experiment: FileExperiment, **kwargs) -> FileSuite:
        """
        Fetches the parent of an experiment.
        Args:
            experiment: File experiment
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
        # Ensure parent
        experiment.parent.add_experiment(experiment)
        self.platform._metas.dump(experiment.parent)
        # Generate/update metadata
        self.platform._metas.dump(experiment)
        # Output
        suite_id = experiment.parent_id or experiment.suite_id
        user_logger.info(f'job_directory: {Path(self.platform.job_directory).resolve()}')
        user_logger.info(f'suite: {str(suite_id)}')
        user_logger.info(f'experiment: {experiment.id}')
        user_logger.info(f"\nExperiment Directory: \n{self.platform.get_directory(experiment)}")

    def post_run_item(self, experiment: Experiment, **kwargs):
        """
        Perform post-processing steps after an experiment run.
        Args:
            experiment: The experiment object that has just finished running
            **kwargs: Additional keyword arguments

        Returns:
            None
        """
        super().post_run_item(experiment, **kwargs)
        # Refresh platform object
        experiment._platform_object = self.get(experiment.id, **kwargs)

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

    def get_assets_from_file_experiment(self, experiment: FileExperiment) -> AssetCollection:
        """
        Get assets for a comps experiment.
        Args:
            experiment: Experiment to get asset collection for.
        Returns:
            AssetCollection if configuration is set and configuration.asset_collection_id is set.
        """
        assets = AssetCollection()
        assets_dir = Path(self.platform.get_directory_by_id(experiment.id, ItemType.EXPERIMENT), 'Assets')
        if assets_dir.exists():
            assets_list = AssetCollection.assets_from_directory(assets_dir, recursive=True)
            for a in assets_list:
                assets.add_asset(a)
        return assets

    def to_entity(self, file_exp: FileExperiment, parent: Optional[Suite] = None, children: bool = True,
                  **kwargs) -> Experiment:
        """
        Convert a FileExperiment  to idmtools Experiment.
        Args:
            file_exp: simulation to convert
            parent: optional experiment object
            children: bool
            kwargs:
        Returns:
            Experiment object
        """
        if parent is None:
            parent = self.platform.get_item(file_exp.parent_id, ItemType.SUITE, force=True)
        exp = Experiment()
        exp.platform = self.platform
        exp.uid = file_exp.uid
        exp.name = file_exp.name
        exp.parent_id = parent.id
        exp.parent = parent
        exp.tags = file_exp.tags
        exp._platform_object = file_exp
        exp.simulations = []

        exp.assets = self.get_assets_from_file_experiment(file_exp)
        if exp.assets is None:
            exp.assets = AssetCollection()

        if children:
            exp.simulations = self.get_children(file_exp, parent=exp, raw=False)

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
        # Refresh status for each simulation
        for sim in experiment.simulations:
            sim.status = self.platform.get_simulation_status(sim.id, **kwargs)

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
        return {sim.id: str(self.platform.get_directory(sim)) for sim in sims}

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
            shutil.rmtree(self.platform.get_directory(exp))
        except RuntimeError:
            logger.info("Could not delete the associated experiment...")
            return

    def platform_cancel(self, experiment_id: str, force: bool = True) -> Any:
        """
        Cancel platform experiment's file job.
        Args:
            experiment_id: experiment id
            force: bool, True/False
        Returns:
            Any
        """
        pass

    def get_assets(self, experiment: Experiment, files: List[str], **kwargs) -> Dict[str, bytearray]:
        """
        Fetch the files associated with an experiment.

        Args:
            experiment: Experiment (idmools Experiment or COMPSExperiment)
            files: List of files to download
            **kwargs:

        Returns:
            Dict[str, Dict[str, Dict[str, str]]]:
                A nested dictionary structured as:
                {
                    experiment.id: {
                        simulation.id {
                            filename: file content as string,
                            ...
                        },
                        ...
                    }
                }
        """
        ret = dict()
        if isinstance(experiment, FileExperiment):
            file_exp = experiment
        else:
            file_exp = experiment.get_platform_object()
        simulations = self.platform.flatten_item(file_exp, raw=True)
        for sim in simulations:
            ret[sim.id] = self.platform._simulations.get_assets(sim, files, **kwargs)
        return ret

    def run_item(self, experiment: Experiment, **kwargs):
        """
        Called during commissioning of an item. This should create the remote resource.

        Args:
            experiment:Experiment
            **kwargs: Keyword arguments to pass to pre_run_item, platform_run_item, post_run_item

        Returns:
            None
        """
        # Consider Suite
        if experiment.parent:
            experiment.parent.add_experiment(experiment)  # may not be necessary
            self.platform._suites.platform_create(experiment.parent)
        super().run_item(experiment, **kwargs)
