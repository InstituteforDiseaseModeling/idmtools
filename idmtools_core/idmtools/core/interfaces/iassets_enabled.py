import typing
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field

from idmtools.assets.asset_collection import AssetCollection

if typing.TYPE_CHECKING:
    from typing import NoReturn
    from idmtools.assets import TAssetCollection, TAsset, TAssetList


@dataclass
class IAssetsEnabled(metaclass=ABCMeta):
    """
    Base class for objects containing an asset collection.
    """
    assets: 'TAssetCollection' = field(default_factory=lambda: AssetCollection(), compare=False,
                                       metadata={"pickle_ignore": True})

    def __post_init__(self):
        pass

    @abstractmethod
    def gather_assets(self) -> 'NoReturn':
        """
        Function called at runtime to gather all assets in the collection.
        """
        pass

    def add_assets(self, assets: 'TAssetList' = None) -> 'NoReturn':
        """
        Add more assets to :class:`~idmtools.assets.asset_collection.AssetCollection`.
        """
        for asset in assets:
            self.assets.add_asset(asset)

    def add_asset(self, asset: 'TAsset' = None) -> 'NoReturn':
        self.assets.add_asset(asset)
