"""
Defines our IWorkflowItem interface.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""

import warnings
from abc import ABC
from dataclasses import dataclass, field, fields, InitVar
from typing import NoReturn, Dict, Any, TYPE_CHECKING
from uuid import UUID
from idmtools.assets import AssetCollection
from idmtools.assets.file_list import FileList
from idmtools.core import ItemType
from idmtools.core.interfaces.iassets_enabled import IAssetsEnabled
from idmtools.core.interfaces.inamed_entity import INamedEntity
from idmtools.core.interfaces.irunnable_entity import IRunnableEntity
from idmtools.entities.itask import ITask

if TYPE_CHECKING:  # pragma: no cover
    from idmtools.entities.iplatform import IPlatform


@dataclass
class IWorkflowItem(IAssetsEnabled, INamedEntity, IRunnableEntity, ABC):
    """
    Interface of idmtools work item.
    """

    #: Name of the workflow step
    name: str = field(default=None)

    #: Legacy name for workflow items
    item_name: InitVar[str] = None
    #: Legacy name. Set assets now
    asset_collection_id: InitVar[UUID] = None
    #: Tags associated with the work item
    tags: Dict[str, Any] = field(default_factory=lambda: {})
    #: Common Assets for the workitem
    transient_assets: AssetCollection = field(default_factory=AssetCollection)
    #: Legacy var. Going forward use assets
    asset_files: InitVar[FileList] = None
    #: Legacy var. Going forward use assets
    user_files: InitVar[FileList] = None
    # Task for object. All workflow items must implement by 1.7.0
    task: ITask = field(default=None)

    related_experiments: list = field(default_factory=list)
    related_simulations: list = field(default_factory=list)
    related_suites: list = field(default_factory=list)
    related_work_items: list = field(default_factory=list)
    related_asset_collections: list = field(default_factory=list)
    work_item_type: str = field(default=None)

    item_type: 'ItemType' = field(default=ItemType.WORKFLOW_ITEM, compare=False, init=False)

    def __post_init__(self, item_name: str, asset_collection_id: UUID, asset_files: FileList, user_files: FileList):
        """
        Constructor.

        Args:
            item_name: Item name
            asset_collection_id: AssetCollectionId
            asset_files: AssetFiles
            user_files: UserFiles

        Returns:
            None
        """
        if item_name is not None and not isinstance(item_name, property):
            self.name = item_name

        if user_files and not isinstance(user_files, property):
            # user property since it can convert file lists
            self.user_files = user_files

        if asset_files and not isinstance(asset_files, property):
            # user property since it can convert file lists
            self.asset_files = asset_files

        if asset_collection_id and not isinstance(asset_collection_id, property):
            # user property since it will inform user of changes
            self.asset_collection_id = asset_collection_id

        if self.task is None:
            warnings.warn("In 1.7.0, all work items require a Task")

        self.tags = self.tags or dict()

    def __repr__(self):
        """
        String representation of workflow items.
        """
        return f"<WorkItem {self.uid}>"

    def gather_assets(self) -> NoReturn:
        """
        Function called at runtime to gather all assets in the collection.
        """
        pass

    def add_file(self, af):
        """
        Methods used to add new file.

        Args:
            af: file to add

        Returns: None
        """
        self.user_files.add_asset_file(af)

    def clear_user_files(self):
        """
        Clear all existing user files.

        Returns: None
        """
        self.transient_assets.clear()

    def pre_creation(self, platform: 'IPlatform') -> None:
        """
        Called before the actual creation of the entity.
        """
        if self.name is None:
            raise ValueError("Name is required")
        files_to_be_removed = ('comps_log.log', 'idmtools.log')
        super().pre_creation(platform)
        if self.task:
            self.task.pre_creation(self, platform)
            self.assets.add_assets(self.task.common_assets)
            self.transient_assets.add_assets(self.task.transient_assets)
        self.transient_assets.files = [f for f in self.transient_assets.assets if f.filename.lower() not in files_to_be_removed]

    def __check_for_platform(self, platform: 'IPlatform'):  # noqa: F821
        """
        Check for platform. If platform is non, we try to load the current platform instead.

        Args:
            platform: Platform that can be pre-defined.

        Returns:
            None

        Raises:
            ValueError - If platform cannot be found
        """
        from idmtools.core.context import CURRENT_PLATFORM
        if platform is not None:
            self.platform = platform
        if self.platform is None:
            if CURRENT_PLATFORM is None:
                raise ValueError("Platform is required to run item")
            self.platform = CURRENT_PLATFORM

    def to_dict(self) -> Dict:
        """
        Convert IWorkflowItem to a dictionary.

        Returns:
            Dictionary of WorkflowItem
        """
        result = dict()
        for f in fields(self):
            if not f.name.startswith("_") and f.name not in ['parent']:
                result[f.name] = getattr(self, f.name)
        result['_uid'] = self.uid
        return result

    @property
    def asset_collection_id(self) -> UUID:
        """
        Alias for legacy code for assets.id. It will be deprecated in 1.7.0.

        Returns:
            Item common assets
        """
        warnings.warn("asset_collection_id will be deprecated in favor of assets in 1.7.0. Set the Assets using AssetCollection.from_id.. going forward", DeprecationWarning)
        return self.assets.id

    @asset_collection_id.setter
    def asset_collection_id(self, value: UUID) -> UUID:
        """
        Error message to notify user of breaking change they must fix now. By 1.7.0, all code must be migrated over.

        Args:
            value:

        Returns:
            None

        Raises:
            ValueError - Method not supported now
        """
        raise ValueError("Setting asset collection id no longer possible. To set ID, use workitem.assets = AssetCollection.from_id(...)")

    @property
    def asset_files(self) -> FileList:
        """
        Alias for legacy code for assets. It will be deprecated in 1.7.0.

        Returns:
            Item common assets
        """
        warnings.warn("asset_files will be deprecated in favor of assets in 1.7.0", DeprecationWarning)
        return FileList.from_asset_collection(self.assets)

    @asset_files.setter
    def asset_files(self, value: FileList):
        """
        Alias for legacy code for assets. It will be deprecated in 1.7.0.

        Returns:
            None
        """
        warnings.warn("asset_files will be deprecated in favor of assets in 1.7.0", DeprecationWarning)
        self.assets = value.to_asset_collection()

    @property
    def item_name(self):
        """
        Alias for legacy code for name. It will be deprecated in 1.7.0.

        Returns:
            name of item
        """
        warnings.warn("Item name will be deprecated in favor of name in 1.7.0", DeprecationWarning)
        return self. name

    @item_name.setter
    def item_name(self, value: str):
        """
        Alias for legacy code for name. It will be deprecated in 1.7.0.

        Returns:
            None
        """
        warnings.warn("Item name will be deprecated in favor of name in 1.7.0", DeprecationWarning)

        self.name = value

    @property
    def user_files(self) -> FileList:
        """
        Alias for legacy code for transient assets. It will be deprecated in 1.7.0.

        Returns:
            File List of transient assets
        """
        warnings.warn("user_files will be deprecated in favor of transient_assets in 1.7.0", DeprecationWarning)
        return FileList.from_asset_collection(self.transient_assets)

    @user_files.setter
    def user_files(self, file_list: FileList):
        """
        Alias for legacy code for transient assets. It will be deprecated in 1.7.0.

        Set transient assets

        Returns:
            None
        """
        self.transient_assets = file_list.to_asset_collection()
