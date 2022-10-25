"""
This module contains all the default filters for the assets.

A filter function needs to take only one argument: an asset. It returns True/False indicating whether to add or filter
out the asset.

You can notice functions taking more than only an asset.
To use those functions, use must create a partial before adding it to a filters list.
For example::

    python
    fname = partial(file_name_is, filenames=["a.txt", "b.txt"])
    AssetCollection.from_directory(... filters=[fname], ...)
"""
import os
import typing

if typing.TYPE_CHECKING:
    from typing import List
    from idmtools.core import TAsset


def default_asset_file_filter(asset: 'TAsset') -> 'bool':
    """
    Default filter to leave out Python caching.

    This filter is used in the creation of
    :class:`~idmtools.assets.asset_collection.AssetCollection`, regardless of user filters.

    Returns:
        True if no files match default patterns of "__py_cache__" and ".pyc"
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

    Returns:
        True if asset.filename in filenames
    """
    return asset.filename in filenames


def file_extension_is(asset: 'TAsset', extensions: 'List[str]') -> 'bool':
    """
    Restrict filtering to assets with the indicated filetypes.

    Args:
        asset: The asset to filter.
        extensions: List of extensions to filter on.

    Returns:
        True if extension in extensions
    """
    return asset.extension in extensions


def asset_in_directory(asset: 'TAsset', directories: 'List[str]', base_path: str = None) -> 'bool':
    """
    Restrict filtering to assets within a given directory.

    This filter is not strict and simply checks if the directory portion is present in the assets absolute path.

    Args:
        asset: The asset to filter.
        directories: List of directory portions to include.
        base_path: base_path
    """
    if base_path is None:
        base_path = os.getcwd()
    norm_base_path = os.path.abspath(base_path)
    norm_dirs = [f"{os.sep}{d}{os.sep}" for d in directories]
    norm_asset_absolute_path = os.path.abspath(asset.absolute_path)
    norm_root = norm_asset_absolute_path.replace(norm_base_path, "")

    if not norm_asset_absolute_path.startswith(norm_base_path):
        return False
    return any([d in norm_root for d in norm_dirs])
