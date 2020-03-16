import copy
import os
import typing
from dataclasses import dataclass, field
from typing import List, NoReturn, TypeVar, Union, Any, Dict

from idmtools.assets import Asset, TAssetList
from idmtools.assets import TAssetFilterList
from idmtools.assets.errors import DuplicatedAssetError
from idmtools.core import FilterMode, ItemType
from idmtools.core.interfaces.ientity import IEntity
from idmtools.utils.entities import get_default_tags
from idmtools.utils.file import scan_directory
from idmtools.utils.filters.asset_filters import default_asset_file_filter

if typing.TYPE_CHECKING:
    from idmtools.assets import TAssetList


@dataclass(repr=False)
class AssetCollection(IEntity):
    """
    A class that represents a collection of assets.

    Args:
        assets: An optional list of assets to create the collection with.
    """

    assets: 'TAssetList' = field(default=None)
    item_type: ItemType = field(default=ItemType.ASSETCOLLECTION, compare=False)

    def __init__(self, assets: List[Asset] = None, tags: Dict[str, Any] = {}):
        """
        A constructor.

        Args: assets: An optional list of assets to create the collection with.
        tags: dict: tags associated with asset collection
        """
        super().__init__()
        self.item_type = ItemType.ASSETCOLLECTION
        self.assets = copy.deepcopy(assets) or []
        self.tags = self.tags or {}

    @classmethod
    def from_directory(cls, assets_directory: str, recursive: bool = True, flatten: bool = False,
                       filters: 'TAssetFilterList' = None, filters_mode: FilterMode = FilterMode.OR,  # noqa: F821
                       relative_path: str = None) -> 'TAssetCollection':
        """
        Fill up an :class:`AssetCollection` from the specified directory. See
        :meth:`~AssetCollection.assets_from_directory` for arguments.

        Returns:
            A created :class:`AssetCollection` object.
        """
        assets = cls.assets_from_directory(assets_directory, recursive, flatten, filters, filters_mode, relative_path)
        return cls(assets=assets)

    # endregion

    @staticmethod
    def assets_from_directory(assets_directory: str, recursive: bool = True, flatten: bool = False,
                              filters: 'TAssetFilterList' = None,  # noqa: F821
                              filters_mode: FilterMode = FilterMode.OR,
                              forced_relative_path: str = None) -> List[Asset]:
        """
        Create assets for files in a given directory.

        Args:
            assets_directory: The root directory of the assets.
            recursive: True to recursively traverse the subdirectory.
            flatten: Put all the files in root regardless of whether they were in a subdirectory or not.
            filters: A list of filters to apply to the assets. The filters are functions taking an
                :class:`~idmtools.assets.asset.Asset` as argument and returning true or false. True adds the asset to
                the collection; False filters it out. See :meth:`~idmtools.utils.filters.asset_filters`.
            filters_mode: When given multiple filters, either OR or AND the results.
            forced_relative_path: Prefix a relative path to the path created from the root directory.

        Examples:
            For **relative_path**, given the following folder structure root/a/1,txt root/b.txt and
            relative_path="test". Will return assets with relative path: test/a/1,txt and test/b.txt

            Given the previous example, if flatten is also set to True, the following relative_path will be set:
            /1.txt and /b.txt

        Returns:
            A list of assets.
        """
        found_assets = []
        for entry in scan_directory(assets_directory, recursive):
            relative_path = os.path.relpath(os.path.dirname(entry.path), assets_directory)
            found_assets.append(Asset(absolute_path=os.path.abspath(entry.path),
                                      relative_path=None if relative_path == "." else relative_path,
                                      filename=entry.name))

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
                asset.relative_path = None

            if forced_relative_path:
                asset.relative_path = os.path.join(forced_relative_path, asset.relative_path)

            assets.append(asset)

        return assets

    def add_directory(self, assets_directory: str, recursive: bool = True, flatten: bool = False,
                      filters: 'TAssetFilterList' = None, filters_mode: FilterMode = FilterMode.OR,  # noqa: F821
                      relative_path: str = None):
        """
        Retrieve assets from the specified directory and add them to the collection.
        See :meth:`~AssetCollection.assets_from_directory` for arguments.
        """
        assets = AssetCollection.assets_from_directory(assets_directory, recursive, flatten, filters, filters_mode,
                                                       relative_path)
        for asset in assets:
            self.add_asset(asset)

    def add_asset(self, asset: Asset, fail_on_duplicate: bool = True):  # noqa: F821
        """
        Add an asset to the collection.

        Args:
           asset: An :class:`~idmtools.assets.asset.Asset` object to add.
           fail_on_duplicate: Raise a **DuplicateAssetError** if an asset is duplicated.
              If not, simply replace it.
        """
        if asset in self.assets:
            if fail_on_duplicate:
                raise DuplicatedAssetError(asset)
            else:
                # The equality not considering the content of the asset, even if it is already present
                # nothing guarantees that the content is the same. So remove and add the fresh one.
                self.assets.remove(asset)
        self.assets.append(asset)

    def __add__(self, other: Union[TAssetList, 'AssetCollection', Asset]) -> 'AssetCollection':
        """
        Allows using the a + b syntax when adding AssetCollections

        Args:
            other: Either a list of assets, an assetcollection, or an asset

        Returns:
            Returns AssetCollection
        """
        if not isinstance(other, (list, AssetCollection, Asset)):
            raise ValueError('You can only items of type AssetCollections, List of Assets, or Assets to a '
                             'AssetCollection')

        na = AssetCollection()
        na.add_assets(self)
        if isinstance(other, Asset):
            na.add_asset(other, True)
        else:
            na.add_assets(other)
        return na

    def add_assets(self, assets: Union[TAssetList, 'AssetCollection'], fail_on_duplicate: bool = True):
        """
        Add assets to a collection

        Args:
            assets: An list of assets as either list or a collection
            fail_on_duplicate: Raise a **DuplicateAssetError** if an asset is duplicated.
              If not, simply replace it.

        Returns:

        """
        for asset in assets:
            self.add_asset(asset, fail_on_duplicate)

    def add_or_replace_asset(self, asset: Asset):
        """
        Add or replaces an asset in a collection

        Args:
            asset: Asset to add or replace

        Returns:
            None.
        """
        index = self.find_index_of_asset(asset.absolute_path, asset.filename)
        if index is not None:
            self.assets[index] = asset
        else:
            self.assets.append(asset)

    def get_one(self, **kwargs):
        """
        Get an asset out of the collection based on the filers passed.

        Examples::

            >>> a = AssetCollection()
            >>> a.get_one(filename="filename.txt")

        Args:
            **kwargs:  keyword argument representing the filters.

        Returns: 
            None or Asset if found.

        """
        try:
            return next(filter(lambda a: all(getattr(a, k) == kwargs.get(k) for k in kwargs), self.assets))
        except StopIteration:
            return None

    def delete(self, **kwargs) -> NoReturn:
        """
        Delete an asset based on keywords attributes

        Args:
            **kwargs: Filter for the asset to delete.
        """
        if 'index' in kwargs:
            return self.assets.remove(self.assets[kwargs.get('index')])

        if 'asset' in kwargs:
            return self.assets.remove(kwargs.get('asset'))

        asset = self.get_one(**kwargs)
        if asset:
            self.assets.remove(asset)

    def pop(self, **kwargs) -> Asset:
        """
        Get and delete an asset based on keywords.

        Args:
            **kwargs: Filter for the asset to pop.

        """
        if not kwargs:
            return self.assets.pop()

        asset = self.get_one(**kwargs)
        if asset:
            self.assets.remove(asset)
        return asset

    def extend(self, assets: List[Asset], fail_on_duplicate: bool = True) -> NoReturn:
        """
        Extend the collection with new assets
        Args:
            assets: Which assets to add
            fail_on_duplicate: Fail if duplicated asset is included.

        """
        for asset in assets:
            self.add_asset(asset, fail_on_duplicate)

    def clear(self):
        self.assets.clear()

    def set_all_persisted(self):
        for a in self:
            a.persisted = True

    @property
    def count(self):
        return len(self.assets)

    @IEntity.uid.getter
    def uid(self):
        if self.count == 0:
            return None
        return super().uid

    def __len__(self):
        return len(self.assets)

    def __getitem__(self, index):
        return self.assets[index]

    def __iter__(self):
        yield from self.assets

    def has_asset(self, absolute_path: str = None, filename: str = None) -> bool:
        """
        Search for asset by absolute_path or by filename

        Args:
            absolute_path: Absolute path of source file
            filename: Destination filename

        Returns:
            True if asset exists, False otherwise
        """
        return self.find_index_of_asset(absolute_path, filename) is not None

    def find_index_of_asset(self, absolute_path: str = None, filename: str = None) -> Union[int, None]:
        """
        Finds the index of asset by path or filename

        Args:
            absolute_path: Path to search
            filename: Filename to search

        Returns:
            Index number if found.
            None if not found.
        """
        for idx, asset in enumerate(self.assets):
            if filename and asset.filename == filename:
                if absolute_path and absolute_path == asset.absolute_path:
                    return idx
                elif absolute_path is None:
                    return idx

            if absolute_path == asset.absolute_path:
                return idx
        return None

    def pre_creation(self) -> None:
        if self.tags:
            self.tags.update(get_default_tags())
        else:
            self.tags = get_default_tags()

    def post_creation(self) -> None:
        pass

    def set_tags(self, tags: Dict[str, Any]):
        self.tags = tags

    def add_tags(self, tags: Dict[str, Any]):
        self.tags.update(tags)


TAssetCollection = TypeVar("TAssetCollection", bound=AssetCollection)
