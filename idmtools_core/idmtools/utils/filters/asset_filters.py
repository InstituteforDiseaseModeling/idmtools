"""
This file contains all the default filters for the Assets.

A filter function needs to take only one argument: an Asset and returns True/False to add/filter out the asset.

You can notice functions taking more than only an `asset`.
To use those functions, the user will have to create a partial before adding it to a filters list.
For example:
```python
fname = partial(file_name_is, filenames=["a.txt", "b.txt"])
AssetCollection.from_directory(... filters=[fname], ...)
```
"""
import typing

if typing.TYPE_CHECKING:
    from typing import List
    from idmtools.core import TAsset


def default_asset_file_filter(asset: 'TAsset') -> 'bool':
    """
    Default filter to leave out python caching.
    This filter is used in the creation of AssetCollection regardless of user filters.
    """
    patterns = [
        "__pycache__",
        ".pyc"
    ]
    return not any([p in asset.absolute_path for p in patterns])


def file_name_is(asset: 'TAsset', filenames: 'List[str]') -> 'bool':
    """
    Filter allowing to only consider assets with a filename contained in the `filenames` list.
    Args:
        asset: The asset to filter
        filenames: List of filenames
    """
    return asset.filename in filenames


def asset_in_directory(asset: 'TAsset', directories: 'List[str]') -> 'bool':
    """
    Filter allowing to only consider assets within a given directory.
    This filter is not strict and simply check if the directory portion is present in the assets absolute path.
    Args:
        asset: The asset to filter
        directories: List of directory portion to include

    """
    return any([d in asset.absolute_path for d in directories])
