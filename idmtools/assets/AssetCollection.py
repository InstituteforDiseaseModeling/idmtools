import os
from typing import List

from assets.Asset import Asset
from entities.IEntity import IEntity
from utils.file import scan_directory
from utils.filters.asset_filters import default_asset_file_filter
from utils.filters.types import AssetFilterList, FilterMode


class AssetCollection(IEntity):
    """
    Represents a collection of Assets
    """

    # region Constructors
    def __init__(self, assets: List[Asset] = None):
        """
        Constructor.
        Args:
            assets: Optional list of assets to create the collection with
        """
        super().__init__()
        self.assets = assets or []

    @classmethod
    def from_directory(cls, assets_directory: str, recursive: bool = True, flatten: bool = False,
                       filters: AssetFilterList = None, filters_mode: FilterMode = FilterMode.OR,
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
    def assets_from_directory(assets_directory: str, recursive: bool = True, flatten: bool = False,
                              filters: AssetFilterList = None, filters_mode: FilterMode = FilterMode.OR,
                              relative_path: str = None) -> List[Asset]:
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
            relative_path: Prefix a relative path to the path created from the root directory

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
        # Create the filters (add the default one to the list)
        filters = filters or []
        filters.append(default_asset_file_filter)

        # Operations on assets (filter, flatten, force relative_path)
        assets = []
        for asset in found_assets:
            results = [f(asset) for f in filters]
            keep_asset = (filters_mode == FilterMode.OR and any(results)) \
                         or (filters_mode == FilterMode.AND and all(results))
            if not keep_asset: continue

            if flatten:
                asset.relative_path = relative_path

            if relative_path:
                asset.relative_path = os.path.join(relative_path, asset.relative_path)

            assets.append(asset)

        return assets

    def add_directory(self, assets_directory: str, recursive: bool = True, flatten: bool = False,
                      filters: AssetFilterList = None, filters_mode: FilterMode = FilterMode.OR,
                      relative_path: str = None):
        """
        Retrieve assets from the specified directory and add them to the collection.
        Args:
            See `AssetCollection.assets_from_directory`.
        """
        assets = self.assets_from_directory(assets_directory, recursive, flatten, filters, filters_mode, relative_path)
        self.assets.extend(assets)

    def add_asset(self, asset: Asset):
        """
        Add an asset to the collection.

        Args:
           asset: An `idmtools.assets.Asset` object to add.
        """
        if asset in self.assets:
            print(f"Asset already present! \n{asset}")
            return
        self.assets.append(asset)
