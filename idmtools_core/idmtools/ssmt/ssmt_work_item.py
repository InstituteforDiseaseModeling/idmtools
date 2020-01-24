import typing
from idmtools.core import TTags
from dataclasses import dataclass, field
from idmtools.core import ItemType
from idmtools.assets.FileList import FileList
from idmtools.entities.iwork_item import IWorkItem
from uuid import UUID

from typing import NoReturn


@dataclass
class SSMTWorkItem(IWorkItem):
    """
    Idm SSMT Work Item
    """

    item_name: str = field(default="Idm SSMT Test")
    command: str = field(default=None)
    item_id: UUID = field(default=None, init=False)
    tags: TTags = field(default_factory=lambda: {})
    asset_collection_id: UUID = field(default=None)
    asset_files: FileList = field(default=None)
    user_files: FileList = field(default=None)
    wo_kwargs: dict = field(default_factory=lambda: {})
    related_experiments: list = field(default=None)

    item_type: 'ItemType' = field(default=ItemType.WorkItem, compare=False, init=False)

    def __post_init__(self):
        self.tags = self.tags or {}
        self.wo_kwargs = self.wo_kwargs or {}
        self.asset_files = self.asset_files or FileList()
        self.user_files = self.user_files or FileList()

    def __repr__(self):
        return f"<WorkItem {self.uid}>"

    def gather_assets(self) -> NoReturn:
        """
        Function called at runtime to gather all assets in the collection.
        """
        pass

    def add_file(self, af):
        """
        Methods used to add new file
        Args:
            af: file to add

        Returns: None
        """
        self.user_files.add_asset_file(af)

    def add_wo_arg(self, name, value):
        """
        Update wo for the name with value
        Args:
            name: wo arg name
            value: wo arg value

        Returns: None
        """
        self.wo_kwargs[name] = value

    def clear_user_files(self):
        """
        Clear all existing user files

        Returns: None
        """
        self.user_files = FileList()

    def clear_wo_args(self):
        """
        Clear all existing wo args

        Returns: None

        """
        self.wo_kwargs = {}


IWorkItemClass = typing.Type[SSMTWorkItem]
