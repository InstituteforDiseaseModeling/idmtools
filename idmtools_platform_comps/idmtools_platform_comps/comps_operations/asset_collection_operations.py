"""idmtools comps asset collections operations.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import os
import uuid
from dataclasses import field, dataclass
from functools import partial
from logging import getLogger, DEBUG
from typing import Type, Union, List, TYPE_CHECKING, Optional
from uuid import UUID
import humanfriendly
from COMPS.Data import AssetCollection as COMPSAssetCollection, QueryCriteria, AssetCollectionFile, SimulationFile, OutputFileMetadata, WorkItemFile
from tqdm import tqdm
from idmtools import IdmConfigParser
from idmtools.assets import AssetCollection, Asset
from idmtools.entities.iplatform_ops.iplatform_asset_collection_operations import IPlatformAssetCollectionOperations
from idmtools_platform_comps.utils.general import get_file_as_generator

if TYPE_CHECKING:  # pragma: no cover
    from idmtools_platform_comps.comps_platform import COMPSPlatform

logger = getLogger(__name__)
user_logger = getLogger("user")


@dataclass
class CompsPlatformAssetCollectionOperations(IPlatformAssetCollectionOperations):
    """
    Provides AssetCollection Operations to COMPSPlatform.
    """
    platform: 'COMPSPlatform'  # noqa F821
    platform_type: Type = field(default=COMPSAssetCollection)

    def get(self, asset_collection_id: Optional[UUID], load_children: Optional[List[str]] = None, query_criteria: Optional[QueryCriteria] = None, **kwargs) -> COMPSAssetCollection:
        """
        Get an asset collection by id.

        Args:
            asset_collection_id: Id of asset collection
            load_children: Optional list of children to load. Defaults to assets and tags
            query_criteria: Optional query_criteria. Ignores children default
            **kwargs:

        Returns:
            COMPSAssetCollection
        """
        children = load_children if load_children is not None else ["assets", "tags"]
        if asset_collection_id is None and query_criteria is None:
            raise ValueError("You cannot query for all asset collections. Please specify a query criteria or an id")
        query_criteria = query_criteria or QueryCriteria().select_children(children)

        return COMPSAssetCollection.get(id=asset_collection_id, query_criteria=query_criteria)

    def platform_create(self, asset_collection: AssetCollection, **kwargs) -> COMPSAssetCollection:
        """
        Create AssetCollection.

        Args:
            asset_collection: AssetCollection to create
            **kwargs:

        Returns:
            COMPSAssetCollection
        """
        ac = COMPSAssetCollection()
        ac_files = set()
        ac_map = dict()
        for asset in asset_collection:
            # using checksum is not accurate and not all systems will support de-duplication
            if asset.checksum is None:
                md5_checksum_str = asset.calculate_checksum()
                ac_files.add(
                    (
                        asset.filename,
                        asset.relative_path,
                        uuid.UUID(md5_checksum_str)
                    )
                )
                ac_map[asset] = uuid.UUID(md5_checksum_str)
            else:  # We should already have this asset so we should have a md5sum
                ac_files.add(
                    (
                        asset.filename,
                        asset.relative_path,
                        asset.checksum if isinstance(asset.checksum, uuid.UUID) else uuid.UUID(asset.checksum)
                    )
                )
                ac_map[asset] = asset.checksum if isinstance(asset.checksum, uuid.UUID) else uuid.UUID(asset.checksum)

        # remove any duplicates
        if logger.isEnabledFor(DEBUG):
            logger.debug(f"Building ac. Filtered out {len(asset_collection) - len(ac_files)} assets that exist on COMPS already")

        for file in ac_files:
            ac.add_asset(AssetCollectionFile(file_name=file[0], relative_path=file[1], md5_checksum=file[2]))
        del ac_files
        # Add tags
        if asset_collection.tags:
            ac.set_tags(asset_collection.tags)

        # check for missing files first
        missing_files = ac.save(return_missing_files=True)
        if missing_files:
            if logger.isEnabledFor(DEBUG):
                logger.debug(f"{len(missing_files)} missing files detected")
            ac2 = COMPSAssetCollection()
            if asset_collection.tags:
                ac2.set_tags(ac.tags)
            total_size = 0
            for asset, cksum in ac_map.items():
                if cksum in missing_files:
                    if asset.absolute_path:
                        total_size += os.path.getsize(asset.absolute_path)
                        ac2.add_asset(
                            AssetCollectionFile(
                                file_name=asset.filename,
                                relative_path=asset.relative_path
                            ),
                            file_path=asset.absolute_path
                        )
                    else:
                        total_size += len(asset.bytes)
                        ac2.add_asset(
                            AssetCollectionFile(
                                file_name=asset.filename,
                                relative_path=asset.relative_path
                            ),
                            data=asset.bytes
                        )
                else:
                    ac2.add_asset(AssetCollectionFile(
                        file_name=asset.filename,
                        relative_path=asset.relative_path,
                        md5_checksum=cksum
                    ))
            if IdmConfigParser.is_output_enabled():
                user_logger.info(f"Uploading {len(missing_files)} files/{humanfriendly.format_size(total_size)}")
            callback = None
            prog = None
            if not IdmConfigParser.is_progress_bar_disabled():
                prog = tqdm(desc="Uploading files", unit='file', total=len(missing_files))

                def update_progress(total_files_uploaded):
                    prog.n = total_files_uploaded
                    prog.display()

                callback = update_progress
            ac2.save(upload_files_callback=callback)
            if callback:
                callback(len(missing_files))
                prog.close()
            ac = ac2
        asset_collection.uid = ac.id
        asset_collection._platform_object = ac
        asset_collection.platform = self.platform
        asset_collection.platform_id = self.platform.uid
        return ac

    def to_entity(self, asset_collection: Union[COMPSAssetCollection, SimulationFile, List[SimulationFile], OutputFileMetadata, List[WorkItemFile]], **kwargs) \
            -> AssetCollection:
        """
        Convert COMPS Asset Collection or Simulation File to IDM Asset Collection.

        Args:
            asset_collection: Comps asset/asset collection to convert to idm asset collection
            **kwargs:

        Returns:
            AssetCollection

        Raises:
            ValueError - If the file is not a SimulationFile or WorkItemFile
        """
        ac = AssetCollection()
        # set the platform/original object
        ac.platform = self.platform
        # we support comps simulations files and experiments as asset collections
        # only true asset collections have ids
        if isinstance(asset_collection, COMPSAssetCollection):
            ac.uid = asset_collection.id
            ac.tags = asset_collection.tags
        elif isinstance(asset_collection, list) and len(asset_collection):
            if not isinstance(asset_collection[0], (SimulationFile, WorkItemFile)):
                raise ValueError("Unknown asset list")
            else:
                for file in asset_collection:
                    ac.add_asset(self.__simulation_file_to_asset(file))
        assets = asset_collection.assets if isinstance(asset_collection, COMPSAssetCollection) else asset_collection
        # if we have just one, make it a list
        if isinstance(asset_collection, SimulationFile):
            ac.add_asset(self.__simulation_file_to_asset(asset_collection))
        if assets:
            # add items to asset collection
            for asset in assets:
                if isinstance(asset, OutputFileMetadata):
                    a = Asset(filename=asset.friendly_name, relative_path=asset.path_from_root, persisted=True)
                else:
                    a = Asset(filename=asset.file_name, checksum=asset.md5_checksum)
                    a._platform_object = asset
                if isinstance(asset_collection, COMPSAssetCollection):
                    a.relative_path = asset.relative_path
                a.persisted = True
                a.length = asset.length
                if isinstance(asset, OutputFileMetadata) or asset.uri:
                    a.download_generator_hook = partial(get_file_as_generator, asset)
                ac.assets.append(a)

        return ac

    def __simulation_file_to_asset(self, asset_collection: Union[SimulationFile, WorkItemFile]):
        """
        Converts a Simulation File to an Asset.

        Args:
            asset_collection:

        Returns:
            Asset created from sim file.
        """
        asset = Asset(filename=asset_collection.file_name, checksum=asset_collection.md5_checksum)
        # set original object for quick access again later
        asset._platform_object = asset_collection
        asset.is_simulation_file = True
        asset.persisted = True
        asset.length = asset_collection.length
        if asset.uri:
            asset.download_generator_hook = partial(get_file_as_generator, asset_collection)
        return asset
