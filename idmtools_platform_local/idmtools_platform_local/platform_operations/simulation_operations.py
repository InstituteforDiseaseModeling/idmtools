import os
from collections import defaultdict
from dataclasses import dataclass
from logging import getLogger, DEBUG
from typing import Dict, List, Set, Union, Iterator, Optional
from uuid import UUID
from docker.models.containers import Container
from tqdm import tqdm
from idmtools.assets import Asset, json
from idmtools.core import ItemType
from idmtools.core.task_factory import TaskFactory
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
from idmtools.entities.iplatform_ops.iplatform_simulation_operations import IPlatformSimulationOperations
from idmtools.entities.simulation import Simulation
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools.utils.collections import ParentIterator
from idmtools.utils.json import IDMJSONEncoder
from idmtools_platform_local.client.simulations_client import SimulationsClient
from idmtools_platform_local.platform_operations.uitils import local_status_to_common, SimulationDict, ExperimentDict

logger = getLogger(__name__)
user_logger = getLogger('user')


@dataclass
class LocalPlatformSimulationOperations(IPlatformSimulationOperations):

    platform: 'LocalPlatform'  # noqa F821
    platform_type: type = SimulationDict

    def get(self, simulation_id: UUID, **kwargs) -> Dict:
        """
        Fetch simulation with specified id
        Args:
            simulation_id: simulation id
            **kwargs:

        Returns:
            SimulationDIct
        """
        return SimulationDict(SimulationsClient.get_one(str(simulation_id)))

    def platform_create(self, simulation: Simulation, **kwargs) -> Dict:
        """
        Create a simulation object

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

        if isinstance(sims, ParentIterator):
            parent_uid = sims.parent.uid
        else:
            parent_uid = sims[0].parent.uid

        final_sims = []

        # pre-creation our simulations
        if isinstance(sims, ParentIterator) and isinstance(sims.items, (TemplatedSimulations, list)):
            sims_i = sims.items
            for simulation in sims_i:
                simulation.pre_creation()
                final_sims.append(simulation)
        elif isinstance(sims, (list, Iterator)):
            for simulation in sims:
                simulation.pre_creation()
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
                simulation.post_creation()
        # copy files to container
        result = self.platform._do.copy_multiple_to_container(worker, items)
        if not result:
            raise IOError("Coping of data for simulations failed.")
        return final_sims

    @staticmethod
    def __create_simulation_metadata(simulation: Simulation):
        """

        Args:
            simulation:

        Returns:

        """
        extra_details = json.loads(json.dumps(simulation.to_dict(), cls=IDMJSONEncoder))
        return extra_details

    def get_parent(self, simulation: SimulationDict, **kwargs) -> ExperimentDict:
        """
        Get the parent of a simulation, aka its experiment

        Args:
            simulation: Simulation to get parent from
            **kwargs:

        Returns:
            ExperimentDict object
        """
        return self.platform.get_item(simulation['experiment_id'], ItemType.EXPERIMENT, raw=True)

    def platform_run_item(self, simulation: Simulation, **kwargs):
        """
        On the local platform, simulations are ran by queue and commissioned through create
        Args:
            simulation:

        Returns:

        """
        pass

    def send_assets(self, simulation: Simulation, worker: Container = None, **kwargs):
        """
        Transfer assets to local sim folder for simulation

        Args:
            simulation: Simulation object
            worker: docker worker containers. Useful in batches

        Returns:

        """
        # Go through all the assets
        path = "/".join(["/data", simulation.experiment.uid, simulation.uid])
        if worker is None:
            worker = self.platform._sm.get('workers')

        items = self._assets_to_copy_multiple_list(path, simulation.assets)
        self.platform._do.copy_multiple_to_container(worker, items)

    def refresh_status(self, simulation: Simulation, **kwargs):
        """
        Refresh status of a sim

        Args:
            simulation:

        Returns:

        """
        latest = self.get(simulation.uid)
        simulation.status = local_status_to_common(latest['status'])

    def get_assets(self, simulation: Simulation, files: List[str], **kwargs) -> Dict[str, bytearray]:
        """
        Get assets for a specific simulation

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
                job_id_path=self.__get_simulation_path(simulation), paths=transients)
            ret = dict(zip(transients, transients_files))

        # Take care of the assets
        if assets:
            asset_path = f'{simulation.parent_id}'
            common_files = self._retrieve_output_files(job_id_path=asset_path, paths=assets)
            ret.update(dict(zip(assets, common_files)))

        return ret

    @staticmethod
    def __get_simulation_path(simulation: Simulation) -> str:
        return f'{simulation.parent_id}/{simulation.uid}'

    def list_assets(self, simulation: Simulation, **kwargs) -> List[Asset]:
        """
        List assets for a sim

        Args:
            simulation: Simulation object

        Returns:

        """
        assets = []
        sim_path = self.__get_simulation_path(simulation)
        full_path = os.path.join(self.platform.host_data_directory, 'workers', sim_path)

        def download_file(filename, buffer_size: int = 128):
            if logger.isEnabledFor(DEBUG):
                logger.debug(f"Streaming file {filename}")
            with open(filename, 'rb') as out:
                while True:
                    chunk = out.read(buffer_size)
                    if chunk:
                        yield chunk
                    else:
                        break
        for root, dirs, files in os.walk(full_path, topdown=False):
            for file in files:
                fp = os.path.join(root, file)
                asset = Asset(filename=file)
                stat = os.stat(fp)
                asset.__length = stat.st_size
                asset.download_generator_hook = lambda: download_file(fp)
                assets.append(asset)
        return assets

    def to_entity(self, simulation: Dict, load_task: bool = False, parent: Optional[Experiment] = None, **kwargs) -> \
            Simulation:
        """
        Convert a sim dict object to an ISimulation

        Args:
            simulation: simulation to convert
            load_task: Load Task Object as well. Can take much longer and have more data on platform
            parent: optional experiment object
            **kwargs:

        Returns:
            ISimulation object
        """
        if parent is None:
            parent = self.platform.get_item(simulation["experiment_id"], ItemType.EXPERIMENT)
        isim = Simulation(task=None)
        isim.platform = self
        isim.experiment = parent
        isim.parent_id = simulation["experiment_id"]
        isim.uid = simulation['simulation_uid']
        isim.tags = simulation['tags']
        isim.status = local_status_to_common(simulation['status'])
        isim.assets = self.list_assets(isim)
        if load_task:
            if ['tags'] in simulation and 'task_type' in simulation['tags']:
                if 'metadata' in simulation['extra_details']:
                    metadata = simulation['extra_details']['metadata']
                else:
                    metadata = dict()

                try:
                    if logger.isEnabledFor(DEBUG):
                        logger.debug(f"Metadata: {metadata}")
                    simulation.task = TaskFactory().create(simulation['tags']['task_type'], **metadata)
                except Exception as e:
                    user_logger.warning(f"Could not load task of type {simulation['tags']['task_type']}. "
                                        f"Received error {str(e)}")
                    logger.exception(e)

                if simulation.task:
                    simulation.task.reload_from_simulation(simulation)
        else:
            metadata = simulation['extra_details']['metadata']
            simulation.task = CommandTask(metadata['command'])

        return isim

    def _retrieve_output_files(self, job_id_path: str, paths: Union[List[str], Set[str]]) -> List[bytes]:
        """
        Retrieves output files
        Args:
            job_id_path: For experiments, this should just be the id. For simulations, the path should be
            experiment_id/simulation id
            paths:

        Returns:

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
        Batch copies a set of items assets to a grouped by path
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
