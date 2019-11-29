import ntpath
from dataclasses import dataclass
from typing import List, Dict, NoReturn
from uuid import UUID

from COMPS.Data import AssetCollection as COMPSAssetCollection, AssetCollectionFile, Experiment as COMPSExperiment, \
    Configuration, SimulationFile
from idmtools.core import CacheEnabled, ItemType
from idmtools.core.interfaces.iitem import IItem
from idmtools.entities import ISimulation, IExperiment
from idmtools.entities.iplatform import IPlatformIOOperations


@dataclass
class COMPSPlatformIOOperations(IPlatformIOOperations, CacheEnabled):

    @staticmethod
    def send_assets_for_experiment(experiment: IExperiment, **kwargs) -> NoReturn:

        if experiment.assets.count == 0:
            return

        ac = COMPSAssetCollection()
        for asset in experiment.assets:
            ac.add_asset(AssetCollectionFile(file_name=asset.filename, relative_path=asset.relative_path),
                         data=asset.bytes)
        ac.save()
        experiment.assets.uid = ac.id
        print("Asset collection for experiment: {}".format(ac.id))

        # associate the assets with the experiment in COMPS
        e = COMPSExperiment.get(id=experiment.uid)
        e.configuration = Configuration(asset_collection_id=ac.id)
        e.save()

    @staticmethod
    def send_assets_for_simulation(simulation, comps_simulation) -> NoReturn:
        for asset in simulation.assets:
            comps_simulation.add_file(simulationfile=SimulationFile(asset.filename, 'input'), data=asset.bytes)

    def send_assets(self, item: 'IItem', **kwargs) -> 'NoReturn':
        # TODO: add asset sending for suites if needed
        if isinstance(item, ISimulation):
            self.send_assets_for_simulation(simulation=item, **kwargs)
        elif isinstance(item, IExperiment):
            self.send_assets_for_experiment(experiment=item, **kwargs)
        else:
            raise Exception(f'Unknown how to send assets for item type: {type(item)} '
                            f'for platform: {self.__class__.__name__}')

    def get_files(self, item: IItem, files: List[str]) -> Dict[str, bytearray]:
        # Retrieve the simulation from COMPS
        comps_simulation = self.parent.metadata.get_platform_item(item.uid, ItemType.SIMULATION,
                                                  columns=["id", "experiment_id"], children=["files", "configuration"])

        all_paths = set(files)
        assets = set(path for path in all_paths if path.lower().startswith("assets"))
        transients = all_paths.difference(assets)

        # Create the return dict
        ret = {}

        # Retrieve the transient if any
        if transients:
            transient_files = comps_simulation.retrieve_output_files(paths=transients)
            ret = dict(zip(transients, transient_files))

        # Take care of the assets
        if assets:
            # Get the collection_id for the simulation
            collection_id = comps_simulation.configuration.asset_collection_id

            # Retrieve the files
            for file_path in assets:
                # Normalize the separators
                normalized_path = ntpath.normpath(file_path)
                ret[file_path] = self.cache.memoize()(self._get_file_for_collection)(collection_id, normalized_path)

        return ret

    def _get_file_for_collection(self, collection_id: UUID, file_path: str) -> NoReturn:
        print(f"Cache miss for {collection_id} {file_path}")

        # retrieve the collection
        ac = self.parent.metadata.get_item(collection_id, ItemType.ASSETCOLLECTION, raw=True)

        # Look for the asset file in the collection
        file_name = ntpath.basename(file_path)
        path = ntpath.dirname(file_path).lstrip(f"Assets\\")

        for asset_file in ac.assets:
            if asset_file.file_name == file_name and (asset_file.relative_path or '') == path:
                return asset_file.retrieve()