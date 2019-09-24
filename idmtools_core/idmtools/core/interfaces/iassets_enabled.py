import typing
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from idmtools.assets import AssetCollection

if typing.TYPE_CHECKING:
    from idmtools.assets import TAssetCollection

@dataclass
class IAssetsEnabled(metaclass=ABCMeta):
    """
    Base class for objects containing an asset collection
    """
    assets: 'TAssetCollection' = field(default_factory=lambda: AssetCollection(), compare=False, metadata={"pickle_ignore": True})

    def __post_init__(self):
        pass

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
