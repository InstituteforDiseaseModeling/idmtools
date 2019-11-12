"""
This module contains all the default filters for the assets.

A filter function needs to take only one argument: an asset. It returns True/False indicating whether to add or filter out the asset.

You can notice functions taking more than only an asset.
To use those functions, use must create a partial before adding it to a filters list.
For example::

    python
    fname = partial(file_name_is, filenames=["a.txt", "b.txt"])
    AssetCollection.from_directory(... filters=[fname], ...)
"""
import typing

if typing.TYPE_CHECKING:
    from typing import List
    from idmtools.core import TAsset


def default_asset_file_filter(asset: 'TAsset') -> 'bool':
    """
    Default filter to leave out Python caching.
    This filter is used in the creation of 
    :class:`~idmtools.assets.asset_collection.AssetCollection`, regardless of user filters.
    """
    patterns = [
        "__pycache__",
        ".pyc"
    ]
    return not any([p in asset.absolute_path for p in patterns])


def file_name_is(asset: 'TAsset', filenames: 'List[str]') -> 'bool':
    """
    Restrict filtering to assets with the indicated filenames. 

    Args:
        asset: The asset to filter.
        filenames: List of filenames to filter on.
    """
    return asset.filename in filenames


def file_extension_is(asset: 'TAsset', extensions: 'List[str]') -> 'bool':
    """
        Restrict filtering to assets with the indicated filetypes.

        Args:
            asset: The asset to filter.
            extensions: List of extensions to filter on.
        """
    return asset.extension in extensions


def asset_in_directory(asset: 'TAsset', directories: 'List[str]') -> 'bool':
    """
    Restrict filtering to assets within a given directory. 
    This filter is not strict and simply checks if the directory portion is present in the assets absolute path.

    Args:
        asset: The asset to filter.
        directories: List of directory portions to include.
    """
    return any([d in asset.absolute_path for d in directories])
