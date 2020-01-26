import os
from collections import defaultdict
from dataclasses import dataclass
from logging import getLogger, DEBUG
from typing import Dict, Any, Tuple, List, Set, Union
from uuid import UUID
from docker.models.containers import Container
from idmtools.core import ItemType
from idmtools.entities import ISimulation
from idmtools.entities.iplatform_ops.iplatform_simulation_operations import IPlatformSimulationOperations
from idmtools_platform_local.client.simulations_client import SimulationsClient
from idmtools_platform_local.platform_operations.uitils import local_status_to_common, SimulationDict, ExperimentDict

logger = getLogger(__name__)


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

    def platform_create(self, simulation: ISimulation, **kwargs) -> Tuple[Any, UUID]:
        """
        Create a simulation object

        Args:
            simulation: Simulation to create
            **kwargs:

        Returns:
            Simulation dict and created id
        """
        from idmtools_platform_local.internals.tasks.create_simulation import CreateSimulationTask

        m = CreateSimulationTask.send(simulation.experiment.uid, simulation.tags)
        id = m.get_result(block=True, timeout=self.platform.default_timeout * 1000)
        s_dict = dict(simulation_uid=id, experiment_id=simulation.experiment.uid, status='CREATED',
                      tags=simulation.tags)
        simulation.uid = id
        self.send_assets(simulation)
        return s_dict, id

    def batch_create(self, sims: List[ISimulation], **kwargs) -> List[Tuple[Any, UUID]]:
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

        m = CreateSimulationsTask.send(sims[0].experiment.uid, [s.tags for s in sims])
        ids = m.get_result(block=True, timeout=self.platform.default_timeout * 1000)

        items = dict()
        # update our uids and then build a list of files to copy
        for i, simulation in enumerate(sims):
            simulation.uid = ids[i]
            path = "/".join(["/data", simulation.experiment.uid, simulation.uid])
            items.update(self._assets_to_copy_multiple_list(path, simulation.assets))
        result = self.platform._do.copy_multiple_to_container(worker, items)
        if not result:
            raise IOError("Coping of data for simulations failed.")
        ids = [(SimulationDict(dict(simulation_uid=id, experiment_id=sims[0].experiment.uid)), id) for id in ids]
        return ids

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

    def platform_run_item(self, simulation: ISimulation):
        """
        On the local platform, simulations are ran by queue and commissioned through create
        Args:
            simulation:

        Returns:

        """
        pass

    def send_assets(self, simulation: ISimulation, worker: Container = None):
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

    def refresh_status(self, simulation: ISimulation):
        """
        Refresh status of a sim

        Args:
            simulation:

        Returns:

        """
        latest = self.get(simulation.uid)
        simulation.status = local_status_to_common(latest['status'])

    def get_assets(self, simulation: ISimulation, files: List[str], **kwargs) -> Dict[str, bytearray]:
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
            sim_path = f'{simulation.parent_id}/{simulation.uid}'
            transients_files = self._retrieve_output_files(job_id_path=sim_path, paths=transients)
            ret = dict(zip(transients, transients_files))

        # Take care of the assets
        if assets:
            asset_path = f'{simulation.parent_id}'
            common_files = self._retrieve_output_files(job_id_path=asset_path, paths=assets)
            ret.update(dict(zip(assets, common_files)))

        return ret

    def list_assets(self, simulation: ISimulation) -> List[str]:
        """
        List assets for a sim

        Args:
            simulation: Simulation object

        Returns:

        """
        raise NotImplementedError("List assets is not yet supported on the LocalPlatform")

    def to_entity(self, simulation: Dict, **kwargs) -> ISimulation:
        """
        Convert a sim dict object to an ISimulation

        Args:
            simulation: simulation to convert
            **kwargs:

        Returns:
            ISimulation object
        """
        experiment = self.platform.get_item(simulation["experiment_id"], ItemType.EXPERIMENT)
        isim = experiment.simulation()
        isim.uid = simulation['simulation_uid']
        isim.tags = simulation['tags']
        isim.status = local_status_to_common(simulation['status'])
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
