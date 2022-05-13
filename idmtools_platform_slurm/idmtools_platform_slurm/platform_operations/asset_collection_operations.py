"""
Here we implement the SlurmPlatform asset collection operations.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import shutil
from uuid import UUID
from pathlib import Path
from dataclasses import field, dataclass
from logging import getLogger
from typing import Type, List, Dict, Union, Optional
from idmtools.assets import AssetCollection, Asset
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools.entities.iplatform_ops.iplatform_asset_collection_operations import IPlatformAssetCollectionOperations

logger = getLogger(__name__)
user_logger = getLogger("user")

EXCLUDE_FILES = ['_run.sh', 'metadata.json', 'stdout.txt', 'stderr.txt', 'status.txt']


@dataclass
class SlurmPlatformAssetCollectionOperations(IPlatformAssetCollectionOperations):
    """
    Provides AssetCollection Operations to SlurmPlatform.
    """
    platform: 'SlurmPlatform'  # noqa F821
    platform_type: Type = field(default=None)

    def get(self, asset_collection_id: Optional[UUID], **kwargs) -> AssetCollection:
        """
        Get an asset collection by id.
        Args:
            asset_collection_id: id of asset collection
            kwargs:
        Returns:
            AssetCollection
        """
        raise NotImplementedError("Get asset collection is not supported on SlurmPlatform.")

    def platform_create(self, asset_collection: AssetCollection, **kwargs) -> AssetCollection:
        """
        Create AssetCollection.
        Args:
            asset_collection: AssetCollection to create
            kwargs:
        Returns:
            AssetCollection
        """
        raise NotImplementedError("platform_create is not supported on SlurmPlatform.")

    def link_common_assets(self, simulation: Simulation, common_asset_dir: Union[Path, str] = None) -> None:
        """
        Link directory/files.
        Args:
            simulation: Simulation
            common_asset_dir: the common asset folder path
        Returns:
            None
        """
        if common_asset_dir is None:
            common_asset_dir = Path(self.platform._op_client.get_entity_dir(simulation.parent), 'Assets')
        link_dir = Path(self.platform._op_client.get_entity_dir(simulation), 'Assets')
        self.platform._op_client.link_dir(common_asset_dir, link_dir)

    def get_assets(self, item: Union[Experiment, Simulation], files: List[str], **kwargs) -> Dict[str, bytearray]:
        """
        Get assets for simulation.
        Args:
            item: Experiment/Simulation
            files: files to be retrieved
            kwargs:
        Returns:
            Dict[str, bytearray]
        """
        ret = dict()
        if isinstance(item, Simulation):
            sim_dir = self.platform._op_client.get_entity_dir(item)
            for file in files:
                asset_file = Path(sim_dir, file)
                if asset_file.exists():
                    asset = Asset(absolute_path=asset_file.absolute())
                    ret[file] = bytearray(asset.bytes)

        return ret

    def list_assets(self, item: Union[Experiment, Simulation], exclude: list[str] = None, **kwargs) -> List[Asset]:
        """
        List assets for Experiment/Simulation.
        Args:
            item: Experiment/Simulation
            exclude: list of file path
            kwargs: extra parameters
        Returns:
            list of Asset
        """
        exclude = exclude or EXCLUDE_FILES
        exclude = [f.lower() for f in exclude]
        assets = []
        if isinstance(item, Experiment):
            assets_dir = Path(self.platform._op_client.get_entity_dir(item), 'Assets')
        elif isinstance(item, Simulation):
            assets_dir = self.platform._op_client.get_entity_dir(item)
        else:
            raise NotImplementedError("List assets for this item is not supported on SlurmPlatform.")

        for asset_file in assets_dir.iterdir():
            if asset_file.is_file() and asset_file.name.lower() not in exclude:
                asset = Asset(absolute_path=asset_file.absolute())
                assets.append(asset)
        return assets

    def copy_asset(self, src: Union[Asset, Path, str], dest: Union[Path, str]) -> None:
        """
        Copy asset/file to destination.
        Args:
            src: the file content
            dest: the file path
        Returns:
            None
        """
        if isinstance(src, Asset):
            if src.absolute_path:
                shutil.copy(src.absolute_path, dest)
            elif src.content:
                with open(Path(dest, src.filename), 'wb') as out:
                    out.write(src.bytes)
        else:
            shutil.copy(src, dest)

    def dump_assets(self, item: Union[Experiment, Simulation], **kwargs) -> None:
        """
        Dump item's assets.
        Args:
            item: Experiment/Simulation
            kwargs: extra parameters
        Returns:
            None
        """
        if isinstance(item, Experiment):
            exp_asset_dir = Path(self.platform._op_client.get_entity_dir(item), 'Assets')
            self.platform._op_client.mk_directory(dest=exp_asset_dir)
            for asset in item.assets:
                self.copy_asset(asset, exp_asset_dir)
        elif isinstance(item, Simulation):
            exp_dir = self.platform._op_client.get_entity_dir(item.parent)
            for asset in item.assets:
                sim_dir = Path(exp_dir, item.id)
                self.copy_asset(asset, sim_dir)
