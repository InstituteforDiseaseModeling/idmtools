import typing
if typing.TYPE_CHECKING:
    from idmtools.core import TAsset


# region Assets Exceptions
class DuplicatedAssetError(Exception):
    def __init__(self, asset: 'TAsset'):
        super().__init__(f"{asset} is already present in the collection!")
