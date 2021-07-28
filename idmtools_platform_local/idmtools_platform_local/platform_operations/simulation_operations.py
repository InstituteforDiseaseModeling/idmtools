"""idmtools local platform simulation operations.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import os
from collections import defaultdict
from dataclasses import dataclass
from functools import partial
from logging import getLogger, DEBUG
from typing import Dict, List, Set, Union, Iterator, Optional, TYPE_CHECKING
from uuid import UUID
from docker.models.containers import Container
from tqdm import tqdm
from idmtools.assets import Asset, json, AssetCollection
from idmtools.core import ItemType
from idmtools.core.task_factory import TaskFactory
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
from idmtools.entities.iplatform_ops.iplatform_simulation_operations import IPlatformSimulationOperations
from idmtools.entities.simulation import Simulation
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools.utils.collections import ExperimentParentIterator
from idmtools.utils.json import IDMJSONEncoder
from idmtools_platform_local.client.simulations_client import SimulationsClient
from idmtools_platform_local.platform_operations.utils import local_status_to_common, SimulationDict, ExperimentDict, download_lp_file

if TYPE_CHECKING:  # pragma: no cover
    from idmtools_platform_local.local_platform import LocalPlatform

logger = getLogger(__name__)
user_logger = getLogger('user')


@dataclass
class LocalPlatformSimulationOperations(IPlatformSimulationOperations):
    """
    Provides Simulation Operations to the Local Platform.
    """
    platform: 'LocalPlatform'  # noqa F821
    platform_type: type = SimulationDict

    def get(self, simulation_id: UUID, **kwargs) -> Dict:
        """
        Fetch simulation with specified id.

        Args:
            simulation_id: simulation id
            **kwargs:

        Returns:
            SimulationDIct
        """
        return SimulationDict(SimulationsClient.get_one(str(simulation_id)))

    def platform_create(self, simulation: Simulation, **kwargs) -> Dict:
        """
        Create a simulation object.

        Args:
            simulation: Simulation to create
            **kwargs:

        Returns:
            Simulation dict and created id
        """
        from idmtools_platform_local.internals.tasks.create_simulation import CreateSimulationTask
        extra_details = self.__create_simulation_metadata(simulation)
        m = CreateSimulationTask.send(simulation.experiment.uid, simulation.tags, extra_details=extra_details)
        if logger.isEnabledFor(DEBUG):
            logger.debug('Creating Simulation ID and directories')
        sim_id = m.get_result(block=True, timeout=self.platform.default_timeout * 1000)
        if logger.isEnabledFor(DEBUG):
            logger.debug('Simulation ID created')
        s_dict = dict(
            simulation_uid=sim_id,
            experiment_id=simulation.experiment.uid,
            status='CREATED',
            tags=simulation.tags
        )
        simulation.uid = sim_id
        self.send_assets(simulation)
        return s_dict

    def batch_create(self, sims: List[Simulation], **kwargs) -> List[SimulationDict]:
        """
        Batch creation of simulations.

        This is optimized by bulk uploading assets after creating of all the assets

        Args:
            sims: List of sims to create
            **kwargs:

        Returns:
            List of SimulationDict object and their IDs
        """
        from idmtools_platform_local.internals.tasks.create_simulation import CreateSimulationsTask
        worker = self.platform._sm.get('workers')

        if isinstance(sims, ExperimentParentIterator):
            parent_uid = sims.parent.uid
        else:
            parent_uid = sims[0].parent.uid

        final_sims = []

        # pre-creation our simulations
        if isinstance(sims, ExperimentParentIterator) and isinstance(sims.items, (TemplatedSimulations, list)):
            sims_i = sims.items
            for simulation in sims_i:
                simulation.pre_creation(self.platform)
                final_sims.append(simulation)
        elif isinstance(sims, (list, Iterator)):
            for simulation in sims:
                simulation.pre_creation(self.platform)
                final_sims.append(simulation)
        else:
            raise ValueError("Needs to be one a list, ParentIterator of TemplatedSimulations or list")

        # first create the sim ids
        sims_to_create = [(s.tags, self.__create_simulation_metadata(s)) for s in final_sims if s.status is None]
        m = CreateSimulationsTask.send(parent_uid, sims_to_create)
        ids = m.get_result(block=True, timeout=self.platform.default_timeout * 1000)

        items = dict()
        # loop over array instead of parent iterator
        if final_sims:
            # update our uids and then build a list of files to copy
            for i, simulation in tqdm(enumerate(final_sims), total=len(final_sims), desc="Finding Simulations Assets"):
                final_sims[i].uid = ids[i]
                path = "/".join(["/data", parent_uid, simulation.uid])
                items.update(self._assets_to_copy_multiple_list(path, simulation.assets))
                simulation.post_creation(self.platform)
        # copy files to container
        result = self.platform._do.copy_multiple_to_container(worker, items)
        if not result:
            raise IOError("Coping of data for simulations failed.")
        return final_sims

    @staticmethod
    def __create_simulation_metadata(simulation: Simulation):
        """
        Encode simulation data to metadata.

        Args:
            simulation: Simulation to encode.

        Returns:
            IDM Metadata.
        """
        extra_details = dict(metadata=json.loads(json.dumps(simulation.to_dict(), cls=IDMJSONEncoder)))
        return extra_details

    def get_parent(self, simulation: SimulationDict, **kwargs) -> ExperimentDict:
        """
        Get the parent of a simulation, aka its experiment.

        Args:
            simulation: Simulation to get parent from
            **kwargs:

        Returns:
            ExperimentDict object
        """
        return self.platform.get_item(simulation['experiment_id'], ItemType.EXPERIMENT, raw=True)

    def platform_run_item(self, simulation: Simulation, **kwargs):
        """
        On the local platform, simulations are ran by queue and commissioned through create.

        Args:
            simulation:

        Returns:
            None
        """
        pass

    def send_assets(self, simulation: Simulation, worker: Container = None, **kwargs):
        """
        Transfer assets to local sim folder for simulation.

        Args:
            simulation: Simulation object
            worker: docker worker containers. Useful in batches

        Returns:
            None
        """
        # Go through all the assets
        path = "/".join(["/data", simulation.experiment.uid, simulation.uid])
        if worker is None:
            worker = self.platform._sm.get('workers')

        items = self._assets_to_copy_multiple_list(path, simulation.assets)
        self.platform._do.copy_multiple_to_container(worker, items)

    def refresh_status(self, simulation: Simulation, **kwargs):
        """
        Refresh status of a sim.

        Args:
            simulation:

        Returns:
            None
        """
        latest = self.get(simulation.uid)
        simulation.status = local_status_to_common(latest['status'])

    def get_assets(self, simulation: Simulation, files: List[str], **kwargs) -> Dict[str, bytearray]:
        """
        Get assets for a specific simulation.

        Args:
            simulation: Simulation object to fetch files for
            files: List of files to fetch

        Returns:
            Returns a dict containing mapping of filename->bytearry
        """
        all_paths = set(files)

        assets = set(path for path in all_paths if path.lower().startswith("assets"))
        transients = all_paths.difference(assets)

        # Create the return dict
        ret = {}

        # Retrieve the transient if any
        if transients:
            transients_files = self._retrieve_output_files(
                job_id_path=self.__get_simulation_path(self.platform, simulation), paths=transients)
            ret = dict(zip(transients, transients_files))

        # Take care of the assets
        if assets:
            asset_path = f'{simulation.parent_id}'
            common_files = self._retrieve_output_files(job_id_path=asset_path, paths=assets)
            ret.update(dict(zip(assets, common_files)))

        return ret

    @staticmethod
    def __get_simulation_path(platform: 'LocalPlatform', simulation: Simulation) -> str:
        """
        Returns the full simulation path on disk.

        Args:
            platform: Platform object(with config)
            simulation: Simulation

        Returns:
            Path to simulation on disk
        """
        os.path.join(platform.host_data_directory, 'workers', str(simulation.parent_id), str(simulation.uid))
        return os.path.join(platform.host_data_directory, 'workers', str(simulation.parent_id), str(simulation.uid))

    def list_assets(self, simulation: Simulation, **kwargs) -> List[Asset]:
        """
        List assets for a sim.

        Args:
            simulation: Simulation object

        Returns:
            List of assets
        """
        assets = []
        sim_path = self.__get_simulation_path(self.platform, simulation)

        for root, _dirs, files in os.walk(sim_path, topdown=False):
            for file in files:
                fp = os.path.join(root, file)
                asset = Asset(filename=file, persisted=True)
                stat = os.stat(fp)
                asset.length = stat.st_size
                asset.download_generator_hook = partial(download_lp_file, fp)
                assets.append(asset)
        return assets

    def to_entity(self, local_sim: Dict, load_task: bool = False, parent: Optional[Experiment] = None, **kwargs) -> \
            Simulation:
        """
        Convert a sim dict object to an ISimulation.

        Args:
            local_sim: simulation to convert
            load_task: Load Task Object as well. Can take much longer and have more data on platform
            parent: optional experiment object
            **kwargs:

        Returns:
            ISimulation object
        """
        if parent is None:
            parent = self.platform.get_item(local_sim["experiment_id"], ItemType.EXPERIMENT)
        simulation = Simulation(task=None)
        simulation.platform = self.platform
        simulation.experiment = parent
        simulation.parent_id = local_sim["experiment_id"]
        simulation.uid = local_sim['simulation_uid']
        simulation.tags = local_sim['tags']
        simulation.status = local_status_to_common(local_sim['status'])
        simulation.task = None

        # load simulation metadata
        metadata = local_sim['extra_details']['metadata']

        # load simulation assets from metadata
        sim_path = self.__get_simulation_path(self.platform, simulation)
        for asset in metadata['assets']:
            self.__convert_json_assets_to_assets(asset, sim_path, simulation.assets)
        # load task if requested
        if load_task and 'tags' in local_sim and 'task_type' in local_sim['tags']:
            try:
                if logger.isEnabledFor(DEBUG):
                    logger.debug(f"Metadata: {metadata}")
                simulation.task = TaskFactory().create(local_sim['tags']['task_type'], **metadata['task'])
            except Exception as e:
                user_logger.warning(f"Could not load task of type {local_sim['tags']['task_type']}. "
                                    f"Received error {str(e)}")
                logger.exception(e)

        # fallback for task
        if simulation.task is None:
            simulation.task = CommandTask(metadata['task']['command'])

        # convert task assets
        for asset_type in ['common_assets', 'transient_assets']:
            ac = AssetCollection()
            for asset in metadata['task'][asset_type]:
                self.__convert_json_assets_to_assets(asset, sim_path, ac)
            setattr(simulation.task, asset_type, ac)
        simulation.task.reload_from_simulation(simulation)
        return simulation

    @staticmethod
    def __convert_json_assets_to_assets(asset: Dict, simulation_path: str, asset_collection: AssetCollection):
        """
        Convert JSON Assets from Metadata to IDM Metadata.

        Args:
            asset: Asset dict
            simulation_path: Path to simulation files
            asset_collection: Asset collection to add asset to

        Returns:
            None. It modifies the passed in asset_collection
        """
        args = dict()
        if 'absolute_path' in asset:
            args['absolute_path'] = asset['absolute_path']
        if 'filename' in asset:
            args['filename'] = asset['filename']
        if 'absolute_path' not in args or args['absolute_path'] is None:
            args['absolute_path'] = os.path.join(simulation_path, args['filename'])
        asset_collection.add_asset(Asset(
            download_generator_hook=partial(download_lp_file, args['absolute_path']),
            **args
        ))

    def _retrieve_output_files(self, job_id_path: str, paths: Union[List[str], Set[str]]) -> List[bytes]:
        """
        Retrieves output files.

        Args:
            job_id_path: For experiments, this should just be the id. For simulations, the path should be
            experiment_id/simulation id
            paths:

        Returns:
            List of output file content
        """
        byte_arrs = []

        for path in paths:
            full_path = os.path.join(self.platform.host_data_directory, 'workers', job_id_path, path)
            full_path = full_path.replace('\\', os.sep).replace('/', os.sep)
            if logger.isEnabledFor(DEBUG):
                logger.debug(f"Retrieving file from {full_path}")
            with open(full_path, 'rb') as fin:
                byte_arrs.append(fin.read())
        return byte_arrs

    def _assets_to_copy_multiple_list(self, path, assets):
        """
        Batch copies a set of items assets to a grouped by path.

        Args:
            path: Target path
            assets: Assets to copy

        Returns:
            Dict of items groups be path.
        """
        items = defaultdict(list)
        for asset in assets:
            file_path = asset.absolute_path
            remote_path = "/".join([path, asset.relative_path]) if asset.relative_path else path
            self.platform._do.create_directory(remote_path)
            opts = dict(dest_name=asset.filename if asset.filename else file_path)
            if file_path:
                opts['file'] = file_path
            else:
                opts['content'] = asset.content
            items[remote_path].append(opts)
        return items
