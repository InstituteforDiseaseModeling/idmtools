"""
The GenericWorkitem when fetches workitems from a server.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from dataclasses import dataclass, InitVar
from idmtools.assets.file_list import FileList
from idmtools.entities.command_task import CommandTask
from idmtools.entities.iworkflow_item import IWorkflowItem


@dataclass
class GenericWorkItem(IWorkflowItem):
    """
    Idm GenericWorkItem.
    """
    command: InitVar[str] = None

    def __post_init__(self, item_name: str, asset_collection_id: str, asset_files: FileList, user_files: FileList, command: str):
        """
        Initialize item.

        Args:
            item_name: Item name to set
            asset_collection_id: Asset Collection ID to use on WorkItem
            asset_files: AssetFiles as file
            user_files: UserFiles to add to WorkItem
            command: Command to run

        Returns:
            None
        """
        self.task = CommandTask(command="See workorder.json")
        super().__post_init__(item_name, asset_collection_id, asset_files, user_files)

    def __hash__(self):
        """
        Hash item.

        Returns:
            Hash id
        """
        return hash(self.id)
