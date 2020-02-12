import json
from abc import ABC
from idmtools.core import TTags
from dataclasses import dataclass, field
from idmtools.core import ItemType
from idmtools.assets.file_list import FileList
from uuid import UUID
from typing import NoReturn
from idmtools.core.interfaces.iassets_enabled import IAssetsEnabled
from idmtools.core.interfaces.inamed_entity import INamedEntity


@dataclass
class IWorkflowItem(IAssetsEnabled, INamedEntity, ABC):
    """
    Interface of idmtools work item
    """

    item_name: str = field(default="Idm WorkItem Test")
    tags: TTags = field(default_factory=lambda: {})
    asset_collection_id: UUID = field(default=None)
    asset_files: FileList = field(default=None)
    user_files: FileList = field(default=None)
    work_order: dict = field(default_factory=lambda: {})
    related_experiments: list = field(default=None)
    related_simulations: list = field(default=None)
    related_suites: list = field(default=None)
    related_work_items: list = field(default=None)
    related_asset_collections: list = field(default=None)
    work_item_type: str = field(default=None)
    plugin_key: str = field(default=None)

    item_type: 'ItemType' = field(default=ItemType.WORKFLOW_ITEM, compare=False, init=False)

    def __post_init__(self):
        self.tags = self.tags or {}
        self.work_order = self.work_order or {}
        self.asset_files = self.asset_files or FileList()
        self.user_files = self.user_files or FileList()

    def __repr__(self):
        return f"<WorkItem {self.uid}>"

    def get_base_work_order(self, platform):
        wi_type = self.work_item_type or platform.work_item_type
        base_wo = {"WorkItem_Type": wi_type}
        return base_wo

    def load_work_order(self, wo_file):
        self.work_order = json.load(open(wo_file, 'rb'))

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

    def set_work_order(self, wo):
        """
        Update wo for the name with value
        Args:
            wo: user wo
        Returns: None
        """
        self.work_order = wo

    def update_work_order(self, name, value):
        """
        Update wo for the name with value
        Args:
            name: wo arg name
            value: wo arg value

        Returns: None
        """
        self.work_order[name] = value

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
        self.work_order = {}
