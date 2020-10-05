from abc import ABC
from dataclasses import dataclass, field, fields
from typing import NoReturn, Dict, Any, TYPE_CHECKING
from uuid import UUID
from idmtools.assets.file_list import FileList
from idmtools.core import ItemType
from idmtools.core.interfaces.iassets_enabled import IAssetsEnabled
from idmtools.core.interfaces.inamed_entity import INamedEntity
from idmtools.core.interfaces.irunnable_entity import IRunnableEntity

if TYPE_CHECKING:
    from idmtools.entities.iplatform import IPlatform


@dataclass
class IWorkflowItem(IAssetsEnabled, INamedEntity, IRunnableEntity, ABC):
    """
    Interface of idmtools work item
    """

    item_name: str = field(default="Idm WorkItem Test")
    tags: Dict[str, Any] = field(default_factory=lambda: {})
    asset_collection_id: UUID = field(default=None)
    asset_files: FileList = field(default=None)
    user_files: FileList = field(default=None)
    related_experiments: list = field(default_factory=list)
    related_simulations: list = field(default_factory=list)
    related_suites: list = field(default_factory=list)
    related_work_items: list = field(default_factory=list)
    related_asset_collections: list = field(default_factory=list)
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

    def pre_creation(self, platform: 'IPlatform') -> None:
        """
        Called before the actual creation of the entity.
        """
        files_to_be_removed = ('comps_log.log', 'idmtools.log')
        self.user_files.files = [f for f in self.user_files.files if f.filename.lower() not in files_to_be_removed]

    def __check_for_platform(self, platform: 'IPlatform'):  # noqa: F821
        from idmtools.core.context import CURRENT_PLATFORM
        if platform is not None:
            self.platform = platform
        if self.platform is None:
            if CURRENT_PLATFORM is None:
                raise ValueError("Platform is required to run item")
            self.platform = CURRENT_PLATFORM

    def run(self, wait_on_done: bool = False, wait_on_done_progress: bool = True,
            platform: 'IPlatform' = None):  # noqa: F821
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

    def wait(self, wait_on_done_progress: bool = True, platform: 'IPlatform' = None):  # noqa: F821
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

    def to_dict(self) -> Dict:
        result = dict()
        for f in fields(self):
            if not f.name.startswith("_") and f.name not in ['parent']:
                result[f.name] = getattr(self, f.name)
        result['_uid'] = self.uid
        return result
