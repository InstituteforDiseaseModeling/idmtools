from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from typing import NoReturn, Union
from idmtools.assets import TAsset, TAssetList
from idmtools.assets.asset_collection import AssetCollection


@dataclass
class IAssetsEnabled(metaclass=ABCMeta):
    """
    Base class for objects containing an asset collection.
    """
    assets: AssetCollection = field(default_factory=lambda: AssetCollection(), compare=False,
                                    metadata={"pickle_ignore": True})

    def __post_init__(self):
        pass

    @abstractmethod
    def gather_assets(self) -> NoReturn:
        """
        Function called at runtime to gather all assets in the collection.
        """
        pass

    def add_assets(self, assets: Union[TAssetList, AssetCollection] = None, fail_on_duplicate: bool = True) -> NoReturn:
        """
        Add more assets to :class:`~idmtools.assets.asset_collection.AssetCollection`.
        """
        for asset in assets:
            self.assets.add_asset(asset, fail_on_duplicate)

    def add_asset(self, asset: Union[str, 'TAsset'] = None, fail_on_duplicate: bool = True) -> NoReturn:
        self.assets.add_asset(asset, fail_on_duplicate)
