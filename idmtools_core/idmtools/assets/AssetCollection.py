import os
import typing

from idmtools.assets import Asset
from idmtools.core.IEntity import IEntity
from idmtools.utils.file import scan_directory
from idmtools.utils.filters.asset_filters import default_asset_file_filter
from idmtools.core import FilterMode

if typing.TYPE_CHECKING:
    from idmtools.core import TAssetList, TAssetFilterList, TAsset


class AssetCollection(IEntity):
    """
    Represents a collection of Assets
    """

    # region Constructors
    def __init__(self, assets: 'TAssetList' = None):
        """
        Constructor.
        Args:
            assets: Optional list of assets to create the collection with
        """
        super().__init__()
        self.assets = assets or []

    @classmethod
    def from_directory(cls, assets_directory: str, recursive: bool = True, flatten: bool = False,
                       filters: 'TAssetFilterList' = None, filters_mode: 'FilterMode' = FilterMode.OR,
                       relative_path: str = None) -> object:
        """
        Fill up an AssetCollection from the specified directory
        Args:
            See `AssetCollection.assets_from_directory`.

        Returns: A created AssetCollection object

        """
        assets = cls.assets_from_directory(assets_directory, recursive, flatten, filters, filters_mode, relative_path)
        return cls(assets=assets)

    # endregion

    def __iter__(self):
        yield from self.assets

    @staticmethod
    def assets_from_directory(assets_directory: 'str', recursive: 'bool' = True, flatten: 'bool' = False,
                              filters: 'TAssetFilterList' = None, filters_mode: 'FilterMode' = FilterMode.OR,
                              forced_relative_path: 'str' = None) -> 'TAssetList':
        """
        Create assets for files in a given directory.

        Args:
            assets_directory: The root directory of the assets.
            recursive:  Recursively traverse sub directory. ON by default
            flatten: Put all the files in root regardless of whether we found them in a sub-directory or not
            filters: A list of filters to apply to the assets. The filters are functions taking an `asset` as argument
            and returning true or false. True: Adding the asset to the collection, False: filter out.
            See `idmtools.utils.filters.asset_filters`
            filters_mode: When given multiple filters, either OR or AND the results
            forced_relative_path: Prefix a relative path to the path created from the root directory

        Examples:
            For relative_path. Given the following folder structure root/a/1,txt root/b.txt and relative_path="test"
            Will return assets with relative path: test/a/1,txt and test/b.txt

            Given the previous example, if flatten is also set to True. The following relative_path will be set:
            /1.txt and /b.txt

        Returns: A list of assets

        """
        found_assets = []
        for entry in scan_directory(assets_directory, recursive):
            relative_path = os.path.dirname(entry.path.replace(assets_directory, "")).strip(os.sep)
            found_assets.append(Asset(absolute_path=os.path.abspath(entry.path),
                                      relative_path=relative_path, filename=entry.name))

        # Apply the default filter
        found_assets = list(filter(default_asset_file_filter, found_assets))

        # Operations on assets (filter, flatten, force relative_path)
        assets = []
        for asset in found_assets:
            if filters:
                results = [f(asset) for f in filters]
                if filters_mode == FilterMode.OR and not any(results):
                    continue
                if filters_mode == FilterMode.AND and not all(results):
                    continue

            if flatten:
                asset.relative_path = forced_relative_path or ""

            if forced_relative_path:
                asset.relative_path = os.path.join(forced_relative_path, asset.relative_path)

            assets.append(asset)

        return assets

    def add_directory(self, assets_directory: 'str', recursive: 'bool' = True, flatten: 'bool' = False,
                      filters: 'TAssetFilterList' = None, filters_mode: 'FilterMode' = FilterMode.OR,
                      relative_path: 'str' = None):
        """
        Retrieve assets from the specified directory and add them to the collection.
        Args:
            See `AssetCollection.assets_from_directory`.
        """
        assets = AssetCollection.assets_from_directory(assets_directory, recursive, flatten, filters, filters_mode,
                                                       relative_path)
        for asset in assets:
            self.add_asset(asset)

    def add_asset(self, asset: 'TAsset'):
        """
        Add an asset to the collection.

        Args:
           asset: An `idmtools.assets.Asset` object to add.
        """
        if asset in self.assets:
            print(f"Asset already present! \n{asset}")
            return
        self.assets.append(asset)
