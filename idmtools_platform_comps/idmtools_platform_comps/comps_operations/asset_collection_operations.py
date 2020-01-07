from dataclasses import field, dataclass
from typing import Any, Type, Tuple
from uuid import UUID
from COMPS.Data import AssetCollection as COMPSAssetCollection, QueryCriteria, AssetCollectionFile

from idmtools.assets import AssetCollection, Asset
from idmtools.entities.iplatform_metadata import IPlatformAssetCollectionOperations


@dataclass
class CompsPlatformAssetCollectionOperations(IPlatformAssetCollectionOperations):
    platform: 'COMPSPlaform'  # noqa F821
    platform_type: Type = field(default=COMPSAssetCollection)

    def get(self, asset_collection_id: UUID, **kwargs) -> COMPSAssetCollection:
        children = kwargs.get('children')
        children = children if children is not None else ["assets"]
        return COMPSAssetCollection.get(id=asset_collection_id, query_criteria=QueryCriteria().select_children(children))

    def create(self, asset_collection: AssetCollection) -> Tuple[COMPSAssetCollection, UUID]:
        ac = COMPSAssetCollection()
        for asset in asset_collection:
            if not asset.persisted:
                ac.add_asset(AssetCollectionFile(file_name=asset.filename, relative_path=asset.relative_path),
                             data=asset.bytes)
            else: # We should already have this asset so we should have a md5sum
                if asset.md5_sum is None:
                    raise Exception("md5sum is None for persisted file!")
                ac.add_asset(AssetCollectionFile(file_name=asset.filename, relative_path=asset.relative_path,
                                                 md5_checksum=asset.md5_sum))
        ac.save()
        asset_collection.uid = ac.id
        return ac, ac.id

    def to_entity(self, asset_collection: COMPSAssetCollection, **kwargs) -> AssetCollection:
        ac = AssetCollection()
        ac.uid = asset_collection.id
        ac.tags = asset_collection.tags
        for asset in asset_collection.assets:
            a = Asset(relative_path=asset.relative_path, filename=asset.file_name, md5sum=asset.md5_checksum)
            a.persisted = True
            ac.assets.append(a)

        return ac
