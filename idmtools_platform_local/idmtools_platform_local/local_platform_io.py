import functools
import logging
import os
from collections import defaultdict
from dataclasses import dataclass
from typing import NoReturn, List, Dict, Any
from docker.models.containers import Container
from idmtools.assets import Asset
from idmtools.core.interfaces.iitem import IItem
from idmtools.entities import ISimulation, IExperiment
from idmtools.entities.iplatform import IPlatformIOOperations
from idmtools.entities.isimulation import TSimulation
from idmtools_platform_local.infrastructure.docker_io import DockerIO
from idmtools_platform_local.infrastructure.service_manager import DockerServiceManager

logger = logging.getLogger(__name__)


@dataclass(init=False)
class LocalPlatformIOOperations(IPlatformIOOperations):
    parent: 'LocalPlatform'
    _do: DockerIO
    _sm: DockerServiceManager

    def __init__(self, parent: 'LocalPlatform', sm: DockerServiceManager):
        self.parent = parent
        self._do = DockerIO(self.parent.host_data_directory)
        self._sm = sm

    def create_directory(self, path) -> bool:
        return self._do.create_directory(path)

    def send_assets(self, item: IItem, **kwargs) -> NoReturn:
        """
                Send assets for item to platform
                """
        if isinstance(item, ISimulation):
            self.send_assets_for_simulation(item, **kwargs)
        elif isinstance(item, IExperiment):
            self.send_assets_for_experiment(item, **kwargs)
        else:
            raise Exception(f'Unknown how to send assets for item type: {type(item)} '
                            f'for platform: {self.__class__.__name__}')

    def send_assets_for_simulation(self, simulation, worker: Container = None):
        """
        Send assets for specified simulation

        Args:
            simulation: Simulation Id
            worker: Options worker container. Useful in batches to reduce overhead

        Returns:
            None
        """
        # Go through all the assets
        path = "/".join(["/data", simulation.experiment.uid, simulation.uid])
        if worker is None:
            worker = self._sm.get('workers')

        items = self.assets_to_copy_multiple_list(path, simulation.assests)
        self._do.copy_multiple_to_container(worker, items)

    def send_asset_to_docker(self, asset: Asset, path: str, worker: Container = None) -> NoReturn:
        """
        Handles sending an asset to docker.

        Args:
            asset: Asset object to send
            path: Path to send find to within docker container
            worker: Optional worker to reduce docker calls

        Returns:
            (NoReturn): Nada
        """
        file_path = asset.absolute_path
        remote_path = "/".join([path, asset.relative_path]) if asset.relative_path else path
        # ensure remote directory exists
        result = self._do.create_directory(remote_path)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Creating directory {remote_path} result: {str(result)}")
        # is it a real file?
        if worker is None:
            worker = self._sm.get('workers')
        src = dict()
        if file_path:
            src['file'] = file_path
        else:
            src['content'] = asset.content
        self._do.copy_to_container(worker, remote_path, dest_name=asset.filename if asset.filename else file_path,
                                   **src)

    def send_assets_for_experiment(self, experiment):
        """
        Sends assets for specified experiment

        Args:
            experiment: Experiment to send assets for

        Returns:
            None
        """
        # Go through all the assets
        path = "/".join(["/data", experiment.uid, "Assets"])
        worker = self._sm.get('workers')
        list(map(functools.partial(self.send_asset_to_docker, path=path, worker=worker), experiment.assets))

    def get_files(self, item: IItem, files: List[str]) -> Dict[str, bytearray]:
        if not isinstance(item, ISimulation):
            raise NotImplementedError("Retrieving files only implemented for Simulations at the moment")

        return self._get_assets_for_simulation(item, files)

    def assets_to_copy_multiple_list(self, path, assets):
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
            self._do.create_directory(remote_path)
            opts = dict(dest_name=asset.filename if asset.filename else file_path)
            if file_path:
                opts['file'] = file_path
            else:
                opts['content'] = asset.content
            items[remote_path].append(opts)
        return items

    def _get_assets_for_simulation(self, simulation: TSimulation, output_files) -> Dict[str, bytearray]:  # noqa: F821
        """
        Get assets for a specific simulation

        Args:
            simulation: Simulation object to fetch files for
            output_files: List of files to fetch

        Returns:
            Returns a dict containing mapping of filename->bytearry
        """
        all_paths = set(output_files)

        assets = set(path for path in all_paths if path.lower().startswith("assets"))
        transients = all_paths.difference(assets)

        # Create the return dict
        ret = {}

        # Retrieve the transient if any
        if transients:
            sim_path = f'{simulation.parent_id}/{simulation.uid}'
            transients_files = self.retrieve_output_files(job_id_path=sim_path, paths=transients)
            ret = dict(zip(transients, transients_files))

        # Take care of the assets
        if assets:
            asset_path = f'{simulation.parent_id}'
            common_files = self.retrieve_output_files(job_id_path=asset_path, paths=assets)
            ret.update(dict(zip(assets, common_files)))

        return ret

    def retrieve_output_files(self, job_id_path, paths):
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
            full_path = os.path.join(self.parent.host_data_directory, 'workers', job_id_path, path)
            full_path = full_path.replace('\\', os.sep).replace('/', os.sep)
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"Retrieving file from {full_path}")
            with open(full_path, 'rb') as fin:
                byte_arrs.append(fin.read())
        return byte_arrs

    def copy_multiple_to_container(self, container: Container, files: Dict[str, Dict[str, Any]],
                                   join_on_copy: bool = True):
        return self._do.copy_multiple_to_container(container, files, join_on_copy)
