import os
import uuid
from dataclasses import field, dataclass
from functools import partial
from hashlib import md5
from logging import getLogger
from typing import Type, Union, List, TYPE_CHECKING, Optional
from uuid import UUID

import humanfriendly
from COMPS.Data import AssetCollection as COMPSAssetCollection, QueryCriteria, AssetCollectionFile, SimulationFile, OutputFileMetadata

from idmtools.assets import AssetCollection, Asset
from idmtools.entities.iplatform_ops.iplatform_asset_collection_operations import IPlatformAssetCollectionOperations
from idmtools.utils.hashing import calculate_md5
from idmtools_platform_comps.utils.general import get_file_as_generator

if TYPE_CHECKING:
    from idmtools_platform_comps.comps_platform import COMPSPlatform

logger = getLogger(__name__)
user_logger = getLogger("user")


@dataclass
class CompsPlatformAssetCollectionOperations(IPlatformAssetCollectionOperations):
    platform: 'COMPSPlatform'  # noqa F821
    platform_type: Type = field(default=COMPSAssetCollection)

    def get(self, asset_collection_id: UUID, load_children: Optional[List[str]] = None,
            query_criteria: Optional[QueryCriteria] = None, **kwargs) -> COMPSAssetCollection:
        """
        Get an asset collection by id

        Args:
            asset_collection_id: Id of asset collection
            load_children: Optional list of children to load. Defaults to assets and tags
            query_criteria: Optional query_criteria. Ignores children default
            **kwargs:

        Returns:
            COMPSAssetCollection
        """
        children = load_children if load_children is not None else ["assets", "tags"]
        query_criteria = query_criteria or QueryCriteria().select_children(children)
        return COMPSAssetCollection.get(id=asset_collection_id, query_criteria=query_criteria)

    def platform_create(self, asset_collection: AssetCollection, **kwargs) -> COMPSAssetCollection:
        """
        Create AssetCollection

        Args:
            asset_collection: AssetCollection to create
            **kwargs:

        Returns:
            COMPSAssetCollection
        """
        ac = COMPSAssetCollection()
        ac_map = dict()
        for asset in asset_collection:
            # using checksum is not accurate and not all systems will support de-duplication
            if asset.checksum is None:

                if asset.absolute_path:
                    cksum = calculate_md5(asset.absolute_path)
                    ac.add_asset(
                        AssetCollectionFile(
                            file_name=asset.filename,
                            relative_path=asset.relative_path,
                            md5_checksum=calculate_md5(asset.absolute_path)
                        )
                    )
                    ac_map[asset] = uuid.UUID(cksum)
                else:
                    md5calc = md5()
                    md5calc.update(asset.bytes)
                    md5_checksum_str = md5calc.hexdigest()
                    ac.add_asset(
                        AssetCollectionFile(
                            file_name=asset.filename,
                            relative_path=asset.relative_path,
                            md5_checksum=md5_checksum_str
                        )
                    )
                    ac_map[asset] = uuid.UUID(md5_checksum_str)
            else:  # We should already have this asset so we should have a md5sum
                ac.add_asset(
                    AssetCollectionFile(
                        file_name=asset.filename,
                        relative_path=asset.relative_path,
                        md5_checksum=asset.checksum
                    )
                )
                ac_map[asset] = asset.checksum

        # Add tags
        if asset_collection.tags:
            ac.set_tags(asset_collection.tags)

        # check for missing files first
        missing_files = ac.save(return_missing_files=True)
        if missing_files:
            ac2 = COMPSAssetCollection()
            total_size = 0
            for asset, cksum in ac_map.items():
                if cksum in missing_files:
                    if asset.absolute_path:
                        total_size += os.path.getsize(asset.absolute_path)
                        ac.add_asset(
                            AssetCollectionFile(
                                file_name=asset.filename,
                                relative_path=asset.relative_path
                            ),
                            file_path=asset.absolute_path
                        )
                    else:
                        total_size += len(asset.bytes)
                        ac.add_asset(
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
            user_logger.info(f"Uploading {len(missing_files)} files/{humanfriendly.format_size(total_size)}")
            ac2.save()
            ac = ac2
        asset_collection.uid = ac.id
        asset_collection._platform_object = asset_collection
        return ac

    def to_entity(self, asset_collection: Union[COMPSAssetCollection, SimulationFile, List[SimulationFile], OutputFileMetadata], **kwargs) \
            -> AssetCollection:
        """
        Convert COMPS Asset Collection or Simulation File to IDM Asset Collection

        Args:
            asset_collection: Comps asset/asset collection to convert to idm asset collection
            **kwargs:

        Returns:
            AssetCollection
        """
        ac = AssetCollection()
        # we support comps simulations files and experiments as asset collections
        # only true asset collections have ids
        if isinstance(asset_collection, COMPSAssetCollection):
            ac.uid = asset_collection.id
            ac.tags = asset_collection.tags
        assets = asset_collection.assets if isinstance(asset_collection, COMPSAssetCollection) else asset_collection
        # if we have just one, make it a list
        if isinstance(asset_collection, SimulationFile):
            asset = Asset(filename=asset_collection.file_name, checksum=asset_collection.md5_checksum)
            asset.is_simulation_file = True
            asset.length = asset_collection.length
            if asset.uri:
                asset.download_generator_hook = partial(get_file_as_generator, asset_collection)
            ac.add_asset(asset)
        if assets:
            # add items to asset collection
            for asset in assets:
                if isinstance(asset, OutputFileMetadata):
                    a = Asset(filename=asset.friendly_name, relative_path=asset.path_from_root)
                else:
                    a = Asset(filename=asset.file_name, checksum=asset.md5_checksum)
                if isinstance(asset_collection, COMPSAssetCollection):
                    a.relative_path = asset.relative_path
                a.persisted = True
                a.length = asset.length
                if isinstance(asset, OutputFileMetadata) or asset.uri:
                    a.download_generator_hook = partial(get_file_as_generator, asset)
                ac.assets.append(a)

        return ac
