from abc import ABCMeta, abstractmethod
import typing

if typing.TYPE_CHECKING:
    from idmtools.core import TAssetCollection


class IAssetsEnabled(metaclass=ABCMeta):
    """
    Base class for objects containing an asset collection
    """

    def __init__(self, assets: 'TAssetCollection' = None, *args, **kwargs):
        from idmtools.assets import AssetCollection
        self.assets = assets or AssetCollection()

    @abstractmethod
    def gather_assets(self) -> None:
        """
        Function called at runtime to gather all assets in the collection.
        """
        pass
