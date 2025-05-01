"""
Here we implement the FilePlatform asset collection operations.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import shutil
from uuid import UUID
from pathlib import Path
from dataclasses import field, dataclass
from logging import getLogger
from typing import TYPE_CHECKING, Type, List, Dict, Union, Optional
from idmtools.core import ItemType
from idmtools.assets import AssetCollection, Asset
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools.entities.iplatform_ops.iplatform_asset_collection_operations import IPlatformAssetCollectionOperations
from idmtools_platform_file.platform_operations.utils import FileSimulation, validate_file_copy_path_length, \
    validate_file_path_length

if TYPE_CHECKING:
    from idmtools_platform_file.file_platform import FilePlatform

logger = getLogger(__name__)
user_logger = getLogger("user")

EXCLUDE_FILES = ['_run.sh', 'metadata.json', 'stdout.txt', 'stderr.txt', 'status.txt', 'job_id.txt', 'job_status.txt']


@dataclass
class FilePlatformAssetCollectionOperations(IPlatformAssetCollectionOperations):
    """
    Provides AssetCollection Operations to FilePlatform.
    """
    platform: 'FilePlatform'  # noqa F821
    platform_type: Type = field(default=None)

    def get(self, asset_collection_id: Optional[UUID], **kwargs) -> AssetCollection:
        """
        Get an asset collection by id.
        Args:
            asset_collection_id: id of asset collection
            kwargs: keyword arguments used to expand functionality.
        Returns:
            AssetCollection
        """
        raise NotImplementedError("Get asset collection is not supported on FilePlatform.")

    def platform_create(self, asset_collection: AssetCollection, **kwargs) -> AssetCollection:
        """
        Create AssetCollection.
        Args:
            asset_collection: AssetCollection to create
            kwargs: keyword arguments used to expand functionality.
        Returns:
            AssetCollection
        """
        raise NotImplementedError("platform_create is not supported on FilePlatform.")

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
            common_asset_dir = Path(self.platform.get_directory(simulation.parent), 'Assets')
        link_dir = Path(self.platform.get_directory(simulation), 'Assets')

        # Copy common assets to simulation directory
        self.platform.link_dir(common_asset_dir, link_dir)

    @staticmethod
    def _get_assets_from_dir(sim_dir: Path, files: List[str]) -> Dict[str, bytearray]:
        ret = {}
        for file in files:
            asset_file = sim_dir / file
            if asset_file.exists():
                asset = Asset(absolute_path=asset_file.absolute())
                ret[file] = bytearray(asset.bytes)
            else:
                raise RuntimeError(f"Couldn't find asset for path '{file}'.")
        return ret

    def get_assets(self, simulation: Union[Simulation, FileSimulation], files: List[str], **kwargs) -> Dict[str, bytearray]:
        """
        Get assets for simulation.
        Args:
            simulation: Simulation or FileSimulation
            files: files to be retrieved
            kwargs: keyword arguments used to expand functionality.
        Returns:
            Dict[str, bytearray]
        """
        if isinstance(simulation, (Simulation, FileSimulation)):
            sim_dir = self.platform.get_directory_by_id(simulation.id, ItemType.SIMULATION)
            return self._get_assets_from_dir(sim_dir, files)
        else:
            raise NotImplementedError(
                f"get_assets() for items of type {type(simulation)} is not supported on FilePlatform.")

    def list_assets(self, item: Union[Experiment, Simulation], exclude: List[str] = None, **kwargs) -> List[Asset]:
        """
        List assets for Experiment/Simulation.
        Args:
            item: Experiment/Simulation
            exclude: list of file path
            kwargs: keyword arguments used to expand functionality.
        Returns:
            list of Asset
        """
        exclude = exclude if exclude is not None else EXCLUDE_FILES
        if isinstance(item, Experiment):
            assets_dir = Path(self.platform.get_directory(item), 'Assets')
            return AssetCollection.assets_from_directory(assets_dir, recursive=True)
        elif isinstance(item, Simulation):
            assets_dir = self.platform.get_directory(item)
            asset_list = AssetCollection.assets_from_directory(assets_dir, recursive=True)
            assets = [asset for asset in asset_list if asset.filename not in exclude]
            return assets
        else:
            raise NotImplementedError("List assets for this item is not supported on FilePlatform.")

    @staticmethod
    def copy_asset(src: Union[Asset, Path, str], dest: Union[Path, str]) -> None:
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
                validate_file_copy_path_length(src.absolute_path, dest)
                shutil.copy(src.absolute_path, dest)
            elif src.content:
                dest_filepath = Path(dest, src.filename)
                validate_file_path_length(dest_filepath)
                dest_filepath.write_bytes(src.bytes)
        else:
            validate_file_copy_path_length(src, dest)
            shutil.copy(src, dest)

    def dump_assets(self, item: Union[Experiment, Simulation], **kwargs) -> None:
        """
        Dump item's assets.
        Args:
            item: Experiment/Simulation
            kwargs: keyword arguments used to expand functionality.
        Returns:
            None
        """
        if isinstance(item, Experiment):
            self.pre_create(item.assets)
            exp_asset_dir = Path(self.platform.get_directory(item), 'Assets')
            self.platform.mk_directory(dest=exp_asset_dir)
            for asset in item.assets:
                self.platform.mk_directory(dest=exp_asset_dir.joinpath(asset.relative_path))
                self.copy_asset(asset, exp_asset_dir.joinpath(asset.relative_path))
            self.post_create(item.assets)
        elif isinstance(item, Simulation):
            self.pre_create(item.assets)
            sim_dir = self.platform.get_directory(item)
            for asset in item.assets:
                self.copy_asset(asset, sim_dir)
            self.post_create(item.assets)
        else:
            raise NotImplementedError(f"dump_assets() for item of type {type(item)} is not supported on FilePlatform.")
