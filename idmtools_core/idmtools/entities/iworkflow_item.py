from abc import ABC
from dataclasses import dataclass, field
from typing import NoReturn, Dict, Any
from uuid import UUID

from idmtools.assets.file_list import FileList
from idmtools.core import ItemType
from idmtools.core.interfaces.iassets_enabled import IAssetsEnabled
from idmtools.core.interfaces.inamed_entity import INamedEntity


@dataclass
class IWorkflowItem(IAssetsEnabled, INamedEntity, ABC):
    """
    Interface of idmtools work item
    """

    item_name: str = field(default="Idm WorkItem Test")
    tags: Dict[str, Any] = field(default_factory=lambda: {})
    asset_collection_id: UUID = field(default=None)
    asset_files: FileList = field(default=None)
    user_files: FileList = field(default=None)
    related_experiments: list = field(default=None)
    related_simulations: list = field(default=None)
    related_suites: list = field(default=None)
    related_work_items: list = field(default=None)
    related_asset_collections: list = field(default=None)
    work_item_type: str = field(default=None)

    item_type: 'ItemType' = field(default=ItemType.WORKFLOW_ITEM, compare=False, init=False)

    def __post_init__(self):
        self.tags = self.tags or {}
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

    def clear_user_files(self):
        """
        Clear all existing user files

        Returns: None
        """
        self.user_files = FileList()

    def pre_creation(self) -> None:
        """
        Called before the actual creation of the entity.
        """
        files_to_be_removed = ('comps_log.log', 'idmtools.log')
        self.user_files.files = [f for f in self.user_files.files if f.filename.lower() not in files_to_be_removed]

    def __check_for_platform(self, platform: 'IPlatform'):
        from idmtools.core.platform_factory import current_platform
        if platform is not None:
            self.platform = platform
        if self.platform is None:
            if current_platform is None:
                raise ValueError("Platform is required to run item")
            self.platform = current_platform


    def run(self, wait_on_done: bool = False, wait_on_done_progress: bool = True, platform: 'IPlatform' = None):
        """
        Run the item on specified platform

        Args:
            wait_on_done: Should we wait on item to finish running? Default is false
            wait_on_done_progress: When waiting, should we try to show progress
            platform: optional platform object

        Returns:

        """
        self.__check_for_platform(platform)
        self.platform.run_items([self])
        if wait_on_done:
            self.wait(wait_on_done_progress)

    def wait(self, wait_on_done_progress: bool = True, platform: 'IPlatform' = None):
        """
        Wait on item to finish

        Args:
            wait_on_done_progress: Should we show progress as we wait?
            platform: Optional platform object

        Returns:

        """
        self.__check_for_platform(platform)
        if wait_on_done_progress:
            self.platform.wait_till_done_progress(self)
        else:
            self.platform.wait_till_done(self)
