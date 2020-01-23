from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Type, Any, List, Tuple, Dict, NoReturn
from uuid import UUID

from idmtools.core import CacheEnabled
from idmtools.entities.iworkflow_item import IWorkflowItem


@dataclass
class IPlatformWorkflowItemOperations(CacheEnabled, ABC):
    platform: 'IPlatform'
    platform_type: Type

    @abstractmethod
    def get(self, workflow_item_id: UUID, **kwargs) -> Any:
        """
        Returns the platform representation of an WorkflowItem

        Args:
            workflow_item_id: Item id of WorkflowItems
            **kwargs:

        Returns:
            Platform Representation of an workflow_item
        """
        pass

    def batch_create(self, workflow_items: List[IWorkflowItem], **kwargs) -> List[Tuple[Any, UUID]]:
        """
        Provides a method to batch create workflow items

        Args:
            workflow_items: List of worfklow items to create
            **kwargs:

        Returns:
            List of tuples containing the create object and id of item that was created
        """
        ret = []
        for wi in workflow_items:
            ret.append(self.create(wi, **kwargs))
        return ret

    def pre_create(self, workflow_item: IWorkflowItem, **kwargs) -> NoReturn:
        """
        Run the platform/workflow item post creation events

        Args:
            workflow_item: IWorkflowItem to run post-creation events
            **kwargs: Optional arguments mainly for extensibility

        Returns:
            NoReturn
        """
        workflow_item.pre_creation()

    def post_create(self, workflow_item: IWorkflowItem, **kwargs) -> NoReturn:
        """
        Run the platform/workflow item post creation events

        Args:
            workflow_item: IWorkflowItem to run post-creation events
            **kwargs: Optional arguments mainly for extensibility

        Returns:
            NoReturn
        """
        workflow_item.post_creation()

    def create(self, workflow_item: IWorkflowItem, do_pre: bool = True, do_post: bool = True, **kwargs):
        """
        Creates an workflow item from an IDMTools IWorkflowItem object. Also performs pre-creation and post-creation
        locally and on platform

        Args:
            workflow_item: Suite to create
            do_pre: Perform Pre creation events for item
            do_post: Perform Post creation events for item
            **kwargs: Optional arguments mainly for extensibility

        Returns:
            Created platform item and the UUID of said item
        """
        if do_pre:
            self.pre_create(workflow_item, **kwargs)
        ret = self.platform_create(workflow_item, **kwargs)
        if do_post:
            self.post_create(workflow_item, **kwargs)
        return ret

    @abstractmethod
    def platform_create(self, workflow_item: IWorkflowItem, **kwargs) -> Tuple[Any, UUID]:
        """
        Creates an workflow_item from an IDMTools workflow_item object

        Args:
            workflow_item: WorkflowItem to create
            **kwargs: Optional arguments mainly for extensibility

        Returns:
            Created platform item and the UUID of said item
        """
        pass

    @abstractmethod
    def get_parent(self, workflow_item: Any, **kwargs) -> Any:
        """
        Returns the parent of item. If the platform doesn't support parents, you should throw a TopLevelItem error

        Args:
            workflow_item:
            **kwargs:

        Returns:

        Raise:
            TopLevelItem
        """
        pass

    @abstractmethod
    def get_children(self, workflow_item: Any, **kwargs) -> List[Any]:
        """
        Returns the children of an workflow_item object

        Args:
            workflow_item: WorkflowItem object
            **kwargs: Optional arguments mainly for extensibility

        Returns:
            Children of workflow_item object
        """
        pass

    def to_entity(self, workflow_item: Any, **kwargs) -> IWorkflowItem:
        """
        Converts the platform representation of workflow_item to idmtools representation

        Args:
            workflow_item:Platform workflow_item object

        Returns:
            IDMTools workflow_item object
        """
        return workflow_item

    @abstractmethod
    def refresh_status(self, workflow_item: IWorkflowItem):
        """
        Refresh status for workflow item
        Args:
            workflow_item: Item to refresh status for

        Returns:
            None
        """
        pass

    @abstractmethod
    def send_assets(self, workflow_item: Any):
        """
        Send assets for workflow item to platform

        Args:
            workflow_item: Item to send assets for

        Returns:

        """
        pass

    @abstractmethod
    def get_assets(self, workflow_item: IWorkflowItem, files: List[str], **kwargs) -> Dict[str, bytearray]:
        """
        Load assets for workflow item
        Args:
            workflow_item: Item
            files: List of files to load
            **kwargs:

        Returns:
            Dictionary with filename as key and value as binary content
        """
        pass

    @abstractmethod
    def list_assets(self, workflow_item: IWorkflowItem) -> List[str]:
        """
        List files available  for workflow item

        Args:
            workflow_item: Workflow item

        Returns:
            List of filenames
        """
        pass