from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field


@dataclass
class IAssetsEnabled(metaclass=ABCMeta):
    """
    Base class for objects containing an asset collection
    """
    assets: 'TAssetCollection' = field(default=None, compare=False)

    def __post_init__(self):
        if not self.assets:
            from idmtools.assets import AssetCollection
            self.assets = AssetCollection()

    @abstractmethod
    def gather_assets(self) -> None:
        """
        Function called at runtime to gather all assets in the collection.
        """
        pass

    def add_assets(self, assets=None) -> None:
        """
        Add more assets to AssetCollection
        """
        for asset in assets:
            self.assets.add_asset(asset)
