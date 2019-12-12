from dataclasses import field, dataclass
from typing import Any, Type
from uuid import UUID
from COMPS.Data import AssetCollection, QueryCriteria
from idmtools.entities.iplatform_metadata import IPlatformAssetCollectionOperations


@dataclass
class CompsPlatformAssetCollectionOperations(IPlatformAssetCollectionOperations):
    platform: 'COMPSPlaform'  # noqa F821
    platform_type: Type = field(default=AssetCollection)

    def get(self, asset_collection_id: UUID, **kwargs) -> Any:
        children = kwargs.get('children')
        children = children if children is not None else ["assets"]
        return AssetCollection.get(id=asset_collection_id, query_criteria=QueryCriteria().select_children(children))
