"""
idmtools assets collection package.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import copy
import os
from dataclasses import dataclass, field
from logging import getLogger
from os import PathLike
from typing import List, NoReturn, TypeVar, Union, Any, Dict, TYPE_CHECKING
from idmtools.assets import Asset, TAssetList
from idmtools.assets import TAssetFilterList
from idmtools.assets.errors import DuplicatedAssetError
from idmtools.core import FilterMode, ItemType
from idmtools.core.interfaces.ientity import IEntity
from idmtools.core.interfaces.iitem import IItem
from idmtools.utils.entities import get_default_tags
from idmtools.utils.file import scan_directory
from idmtools.utils.filters.asset_filters import default_asset_file_filter
from idmtools.utils.info import get_doc_base_url

IGNORE_DIRECTORIES = ['.git', '.svn', '.venv', '.idea', '.Rproj.user', '$RECYCLE.BIN', '__pycache__']

if TYPE_CHECKING:  # pragma: no cover
    from idmtools.entities.iplatform import IPlatform

user_logger = getLogger('user')


@dataclass(repr=False)
class AssetCollection(IEntity):
    """
    A class that represents a collection of assets.
    """

    #: Assets for collection
    assets: List[Asset] = field(default=None)
    #: ItemType so platform knows how to handle item properly
    item_type: ItemType = field(default=ItemType.ASSETCOLLECTION, compare=False)

    def __init__(self, assets: Union[List[str], TAssetList, 'AssetCollection'] = None, tags=None):
        """
        A constructor.

        Args: assets: An optional list of assets to create the collection with.
        tags: dict: tags associated with asset collection
        """
        super().__init__()
        if tags is None:
            tags = {}
        self.item_type = ItemType.ASSETCOLLECTION
        if isinstance(assets, AssetCollection):
            self.assets = copy.deepcopy(assets.assets)
        elif assets:
            self.assets = []
            for asset in assets:
                self.add_or_replace_asset(asset)
        else:
            self.assets = []

        self.tags = self.tags or tags

    @classmethod
    def from_id(cls, item_id: str, platform: 'IPlatform' = None, as_copy: bool = False,  # noqa E821
                **kwargs) -> 'AssetCollection':
        """
        Loads a AssetCollection from id.

        Args:
            item_id: Asset Collection ID
            platform: Platform Object
            as_copy: Should you load the object as a copy. When True, the contents of AC are copied, but not the id. Useful when editing ACs
            **kwargs:

        Returns:
            AssetCollection
        """
        if item_id is None:
            raise ValueError("You must specify an id")
        item = super(AssetCollection, cls).from_id(item_id, platform, **kwargs)
        return AssetCollection(item) if as_copy else item

    @classmethod
    def from_directory(cls, assets_directory: str, recursive: bool = True, flatten: bool = False,
                       filters: 'TAssetFilterList' = None, filters_mode: FilterMode = FilterMode.OR,  # noqa: F821
                       relative_path: str = None) -> 'TAssetCollection':
        """
        Fill up an :class:`AssetCollection` from the specified directory.

        See :meth:`~AssetCollection.assets_from_directory` for arguments.

        Returns:
            A created :class:`AssetCollection` object.
        """
        assets = cls.assets_from_directory(assets_directory, recursive, flatten, filters, filters_mode, relative_path)
        return cls(assets=assets)

    @staticmethod
    def assets_from_directory(assets_directory: Union[str, PathLike], recursive: bool = True, flatten: bool = False,
                              filters: 'TAssetFilterList' = None,  # noqa: F821
                              filters_mode: FilterMode = FilterMode.OR,
                              forced_relative_path: str = None, no_ignore: bool = False) -> List[Asset]:
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
            no_ignore: Should we not ignore common directories(.git, .svn. etc) The full list is defined in IGNORE_DIRECTORIES

        Examples:
            For **relative_path**, given the following folder structure root/a/1,txt root/b.txt and
            relative_path="test". Will return assets with relative path: test/a/1,txt and test/b.txt

            Given the previous example, if flatten is also set to True, the following relative_path will be set:
            /1.txt and /b.txt

        Returns:
            A list of assets.
        """
        if isinstance(assets_directory, PathLike):
            assets_directory = str(assets_directory)
        found_assets = []
        for entry in scan_directory(assets_directory, recursive, IGNORE_DIRECTORIES if not no_ignore else None):
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

    def copy(self) -> 'AssetCollection':
        """
        Copy our Asset Collection, removing ID and tags.

        Returns:
            New AssetCollection containing Assets from other AssetCollection
        """
        return AssetCollection(self)

    def add_directory(self, assets_directory: Union[str, PathLike], recursive: bool = True, flatten: bool = False,
                      filters: 'TAssetFilterList' = None, filters_mode: FilterMode = FilterMode.OR,  # noqa: F821
                      relative_path: str = None, no_ignore: bool = False):
        """
        Retrieve assets from the specified directory and add them to the collection.

        See :meth:`~AssetCollection.assets_from_directory` for arguments.
        """
        if isinstance(assets_directory, PathLike):
            assets_directory = str(assets_directory)
        assets = AssetCollection.assets_from_directory(assets_directory, recursive, flatten, filters, filters_mode, relative_path, no_ignore)
        for asset in assets:
            self.add_asset(asset)

    def is_editable(self, error=False) -> bool:
        """
        Checks whether Item is editable.

        Args:
            error: Throw error is not

        Returns:
            True if editable, False otherwise.
        """
        if self.platform_id:
            if error:
                raise ValueError(
                    f"You cannot modify an already provisioned Asset Collection. If you want to modify an existing AssetCollection see the recipe {get_doc_base_url()}cookbook/assets.html#modifying-asset-collection")
            return False
        return True

    def add_asset(self, asset: Union[Asset, str, PathLike], fail_on_duplicate: bool = True, fail_on_deep_comparison: bool = False, **kwargs):  # noqa: F821
        """
        Add an asset to the collection.

        Args:
           asset: A string or an :class:`~idmtools.assets.asset.Asset` object to add. If a string, the string will be
            used as the absolute_path and any kwargs will be passed to the Asset constructor
           fail_on_duplicate: Raise a **DuplicateAssetError** if an asset is duplicated.
             If not, simply replace it.
           fail_on_deep_comparison: Fails only if deep comparison differs
           **kwargs: Arguments to pass to Asset constructor when asset is a string

        Raises:
            DuplicatedAssetError - If fail_on_duplicate is true and the asset is already part of the collection
        """
        self.is_editable(True)
        if isinstance(asset, (str, PathLike)):
            asset = Asset(absolute_path=str(asset), **kwargs)
        # do a simple check first
        if asset in self.assets:
            if fail_on_duplicate:
                if not fail_on_deep_comparison or self.find_index_of_asset(asset, deep_compare=True) is None:
                    raise DuplicatedAssetError(("File with same paths but different content provided", asset) if fail_on_deep_comparison else asset)
            else:
                # The equality not considering the content of the asset, even if it is already present
                # nothing guarantees that the content is the same. So remove and add the fresh one.
                self.assets.remove(asset)
        self.assets.append(asset)

    def __add__(self, other: Union[TAssetList, 'AssetCollection', Asset]) -> 'AssetCollection':
        """
        Allows using the a + b syntax when adding AssetCollections.

        Args:
            other: Either a list of assets, an assetcollection, or an asset

        Returns:
            Returns AssetCollection
        """
        if not isinstance(other, (list, AssetCollection, Asset)):
            raise ValueError('You can only items of type AssetCollections, List of Assets, or Assets to a '
                             'AssetCollection')
        self.is_editable(True)
        na = AssetCollection()
        na.add_assets(self)
        if isinstance(other, Asset):
            na.add_asset(other, False)
        else:
            if len(self.assets) == 0:
                na.assets = copy.deepcopy(other.assets)
                return na
            na.add_assets(other, False)
        return na

    def add_assets(self, assets: Union[TAssetList, 'AssetCollection'], fail_on_duplicate: bool = True, fail_on_deep_comparison: bool = False):
        """
        Add assets to a collection.

        Args:
            assets: An list of assets as either list or a collection
            fail_on_duplicate: Raise a **DuplicateAssetError** if an asset is duplicated.
              If not, simply replace it.
            fail_on_deep_comparison: Fail if relative path/file is same but contents differ

        Returns:
            None
        """
        self.is_editable(True)
        for asset in assets:
            self.add_asset(asset, fail_on_duplicate, fail_on_deep_comparison)

    def add_or_replace_asset(self, asset: Union[Asset, str, PathLike], fail_on_deep_comparison: bool = False):
        """
        Add or replaces an asset in a collection.

        Args:
            asset: Asset to add or replace
            fail_on_deep_comparison: Fail replace if contents differ

        Returns:
            None.
        """
        self.is_editable(True)
        tasset = Asset(asset) if isinstance(asset, (str, PathLike)) else asset
        index = self.find_index_of_asset(tasset)
        if index is not None:
            if fail_on_deep_comparison and not tasset.deep_equals(self.assets[index]):
                raise ValueError(f"Contents of file {asset.short_remote_path()} being replaced differs. To prevent unexpected behaviour, please review script or disable deep checks")
            self.assets[index] = tasset
        else:
            self.assets.append(tasset)

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

    def remove(self, **kwargs) -> NoReturn:
        """
        Remove an asset from the AssetCollection based on keywords attributes.

        Args:
            **kwargs: Filter for the asset to remove.
        """
        self.is_editable(True)
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
        self.is_editable(True)
        if not kwargs:
            return self.assets.pop()

        asset = self.get_one(**kwargs)
        if asset:
            self.assets.remove(asset)
        return asset

    def extend(self, assets: List[Asset], fail_on_duplicate: bool = True) -> NoReturn:
        """
        Extend the collection with new assets.

        Args:
            assets: Which assets to add
            fail_on_duplicate: Fail if duplicated asset is included.

        """
        self.is_editable(True)
        for asset in assets:
            self.add_asset(asset, fail_on_duplicate)

    def clear(self):
        """
        Clear the asset collection.

        Returns:
            None
        """
        self.is_editable(True)
        self.assets.clear()

    def set_all_persisted(self):
        """
        Set all persisted.

        Returns:
            None
        """
        for a in self:
            a.persisted = True

    @property
    def count(self):
        """
        Number of assets in collections.

        Returns:
            Total assets
        """
        return len(self.assets)

    @IEntity.uid.getter
    def uid(self):
        """
        Uid of Asset Collection.

        Returns:
            Asset Collection UID.
        """
        if self.count == 0:
            return None
        return super().uid

    def __len__(self):
        """
        Length of the asset collection(number of assets).

        Returns:
            Total number of assets
        """
        return len(self.assets)

    def __getitem__(self, index):
        """
        Get item from assets collection.

        Args:
            index: Index to load

        Returns:
            Asset at the index.
        """
        return self.assets[index]

    def __iter__(self):
        """
        Allow asset collection to be iterable.

        Returns:
            Iterator of assets
        """
        yield from self.assets

    def has_asset(self, absolute_path: str = None, filename: str = None, relative_path: str = None, checksum: str = None) -> bool:
        """
        Search for asset by absolute_path or by filename.

        Args:
            absolute_path: Absolute path of source file
            filename: Destination filename
            relative_path: Relative path of asset
            checksum: Checksum of asset(optional)

        Returns:
            True if asset exists, False otherwise
        """
        # make a dummy asset
        content = None if absolute_path or checksum else ""
        tmp_asset = Asset(absolute_path=absolute_path, filename=filename, relative_path=relative_path, checksum=checksum, content=content)
        return self.find_index_of_asset(tmp_asset) is not None

    def find_index_of_asset(self, other: 'Asset', deep_compare: bool = False) -> Union[int, None]:
        """
        Finds the index of asset by path or filename.

        Args:
            other: Other asset
            deep_compare: Should content as well as path be compared

        Returns:
            Index number if found.
            None if not found.
        """
        for idx, asset in enumerate(self.assets):
            if deep_compare and asset.deep_equals(other):
                return idx
            elif not deep_compare and asset == other:
                return idx
        return None

    def pre_creation(self, platform: 'IPlatform') -> None:
        """
        Pre-Creation hook for the asset collection.

        Args:
            platform: Platform object we are create asset collection on

        Returns:
            None

        Notes:
            TODO - Make default tags optional
        """
        if self.tags:
            self.tags.update(get_default_tags())
        else:
            self.tags = get_default_tags()
        IItem.pre_creation(self, platform)

    def set_tags(self, tags: Dict[str, Any]):
        """
        Set the tags on the asset collection.

        Args:
            tags: Tags to set on the item

        Returns:
            None
        """
        self.tags = tags

    def add_tags(self, tags: Dict[str, Any]):
        """
        Add tags to the Asset collection.

        Args:
            tags: Tags to add

        Returns:
            None
        """
        self.tags.update(tags)


TAssetCollection = TypeVar("TAssetCollection", bound=AssetCollection)
