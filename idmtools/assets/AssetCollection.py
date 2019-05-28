import os
from typing import List

from assets.Asset import Asset
from utils.file import scan_directory
from utils.filters.asset_filters import default_asset_file_filter
from utils.filters.types import AssetFilterList, FilterMode


class AssetCollection:

    # region Constructors
    def __init__(self, assets: List[Asset] = None):
        self.assets = assets or []

    @classmethod
    def from_directory(cls, assets_directory: str, recursive: bool = True) -> object:
        assets = cls.assets_from_directory(assets_directory, recursive)
        return cls(assets=assets)

    # endregion

    def __iter__(self):
        yield from self.assets

    @staticmethod
    def assets_from_directory(assets_directory: str, recursive: bool = True) -> List[Asset]:
        assets = []
        for entry in scan_directory(assets_directory, recursive):
            relative_path = os.path.dirname(entry.path.replace(assets_directory, "")).strip(os.sep)
            assets.append(Asset(absolute_path=os.path.abspath(entry.path),
                                relative_path=relative_path, filename=entry.name))
        return assets

    def add_asset(self, asset:Asset):
        if asset in self.assets:
            print(f"Asset already present! \n{asset}")
            return
        self.assets.append(asset)

    def add_directory(self, assets_directory: str, recursive: bool = True, flatten: bool = False,
                      filters: AssetFilterList = None, filters_mode: FilterMode = FilterMode.OR,
                      relative_path: str = None):

        # Retrieve all the assets of the directory
        assets = self.assets_from_directory(assets_directory, recursive)

        # Create the filters (add the default one to the list)
        filters = filters or []
        filters.append(default_asset_file_filter)

        # Operations on assets (filter, flatten, force relative_path)
        for asset in assets:
            results = [f(asset) for f in filters]
            keep_asset = (filters_mode == FilterMode.OR and any(results)) \
                         or (filters_mode == FilterMode.AND and all(results))
            if not keep_asset: continue

            if flatten:
                asset.relative_path = relative_path

            if relative_path:
                asset.relative_path = os.path.join(relative_path, asset.relative_path)

            self.add_asset(asset)
