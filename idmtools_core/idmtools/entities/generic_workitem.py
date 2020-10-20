from dataclasses import dataclass, InitVar
from uuid import UUID
from idmtools.assets.file_list import FileList
from idmtools.entities.command_task import CommandTask
from idmtools.entities.iworkflow_item import IWorkflowItem


@dataclass
class GenericWorkItem(IWorkflowItem):
    command: InitVar[str] = None
    """
    Idm GenericWorkItem
    """
    def __post_init__(self, item_name: str, asset_collection_id: UUID, asset_files: FileList, user_files: FileList, command: str):
        self.task = CommandTask(command=command)
        super().__post_init__(item_name, asset_collection_id, asset_files, user_files)

    def __hash__(self):
        return hash(self.id)
