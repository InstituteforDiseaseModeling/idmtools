from abc import ABCMeta, abstractmethod
import typing

from idmtools.utils.decorators import pickle_ignore_fields

if typing.TYPE_CHECKING:
    from idmtools.core import TAssetCollection


@pickle_ignore_fields(["assets"])
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
