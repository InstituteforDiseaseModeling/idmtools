"""
IPlatformWorkflowItemOperations defines workflow item operations interface.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from logging import DEBUG
from typing import Type, Any, List, Tuple, Dict, NoReturn, TYPE_CHECKING
from idmtools.assets import Asset
from idmtools.core import CacheEnabled, getLogger
from idmtools.entities.iplatform_ops.utils import batch_create_items
from idmtools.entities.iworkflow_item import IWorkflowItem
from idmtools.registry.functions import FunctionPluginManager

if TYPE_CHECKING:  # pragma: no cover
    from idmtools.entities.iplatform import IPlatform

logger = getLogger(__name__)


@dataclass
class IPlatformWorkflowItemOperations(CacheEnabled, ABC):
    """
    IPlatformWorkflowItemOperations defines workflow item operations interface.
    """
    platform: 'IPlatform'  # noqa: F821
    platform_type: Type

    @abstractmethod
    def get(self, workflow_item_id: str, **kwargs) -> Any:
        """
        Returns the platform representation of an WorkflowItem.

        Args:
            workflow_item_id: Item id of WorkflowItems
            **kwargs:

        Returns:
            Platform Representation of an workflow_item
        """
        pass

    def batch_create(self, workflow_items: List[IWorkflowItem], display_progress: bool = True, **kwargs) -> List[Any]:
        """
        Provides a method to batch create workflow items.

        Args:
            workflow_items: List of worfklow items to create
            display_progress: Whether to display progress bar
            **kwargs:

        Returns:
            List of tuples containing the create object and id of item that was created.
        """
        return batch_create_items(workflow_items, create_func=self.create, display_progress=display_progress,
                                  progress_description="Creating WorkItems", unit="workitem", **kwargs)

    def pre_create(self, workflow_item: IWorkflowItem, **kwargs) -> NoReturn:
        """
        Run the platform/workflow item post creation events.

        Args:
            workflow_item: IWorkflowItem to run post-creation events
            **kwargs: Optional arguments mainly for extensibility

        Returns:
            NoReturn
        """
        if logger.isEnabledFor(DEBUG):
            logger.debug("Calling idmtools_platform_pre_create_item")
        FunctionPluginManager.instance().hook.idmtools_platform_pre_create_item(item=workflow_item, kwargs=kwargs)
        if logger.isEnabledFor(DEBUG):
            logger.debug("Calling pre_creation")
        workflow_item.pre_creation(self.platform)

    def post_create(self, workflow_item: IWorkflowItem, **kwargs) -> NoReturn:
        """
        Run the platform/workflow item post creation events.

        Args:
            workflow_item: IWorkflowItem to run post-creation events
            **kwargs: Optional arguments mainly for extensibility

        Returns:
            NoReturn
        """
        if logger.isEnabledFor(DEBUG):
            logger.debug("Calling idmtools_platform_post_create_item hooks")
        FunctionPluginManager.instance().hook.idmtools_platform_post_create_item(item=workflow_item, kwargs=kwargs)
        if logger.isEnabledFor(DEBUG):
            logger.debug("Calling post_creation")
        workflow_item.post_creation(self.platform)

    def create(self, workflow_item: IWorkflowItem, do_pre: bool = True, do_post: bool = True, **kwargs) -> Any:
        """
        Creates an workflow item from an IDMTools IWorkflowItem object.

        Also performs pre-creation and post-creation locally and on platform.

        Args:
            workflow_item: Suite to create
            do_pre: Perform Pre creation events for item
            do_post: Perform Post creation events for item
            **kwargs: Optional arguments mainly for extensibility

        Returns:
            Created platform item and the UUID of said item
        """
        if workflow_item.status is not None:
            return workflow_item._platform_object, workflow_item.uid
        if do_pre:
            if logger.isEnabledFor(DEBUG):
                logger.debug("Calling pre_create")
            self.pre_create(workflow_item, **kwargs)
        if logger.isEnabledFor(DEBUG):
            logger.debug("Calling platform_create")
        ret = self.platform_create(workflow_item, **kwargs)
        workflow_item.platform = self.platform
        if do_post:
            if logger.isEnabledFor(DEBUG):
                logger.debug("Calling post_create")
            self.post_create(workflow_item, **kwargs)
        return ret

    @abstractmethod
    def platform_create(self, workflow_item: IWorkflowItem, **kwargs) -> Tuple[Any, str]:
        """
        Creates an workflow_item from an IDMTools workflow_item object.

        Args:
            workflow_item: WorkflowItem to create
            **kwargs: Optional arguments mainly for extensibility

        Returns:
            Created platform item and the id of said item
        """
        pass

    def pre_run_item(self, workflow_item: IWorkflowItem, **kwargs):
        """
        Trigger right before commissioning experiment on platform.

        This ensures that the item is created. It also ensures that the children(simulations) have also been created.

        Args:
            workflow_item: Experiment to commission

        Returns:
            None
        """
        # ensure the item is created before running
        # TODO what status are valid here? Create only?
        if workflow_item.status is None:
            if logger.isEnabledFor(DEBUG):
                logger.debug("Calling create")
            self.create(workflow_item)

    def post_run_item(self, workflow_item: IWorkflowItem, **kwargs):
        """
        Trigger right after commissioning workflow item on platform.

        Args:
            workflow_item: Experiment just commissioned

        Returns:
            None
        """
        if logger.isEnabledFor(DEBUG):
            logger.debug("Calling idmtools_platform_post_run hooks")
        FunctionPluginManager.instance().hook.idmtools_platform_post_run(item=workflow_item, kwargs=kwargs)

    def run_item(self, workflow_item: IWorkflowItem, **kwargs):
        """
        Called during commissioning of an item. This should create the remote resource.

        Args:
            workflow_item:

        Returns:
            None
        """
        if logger.isEnabledFor(DEBUG):
            logger.debug("Calling pre_run_item")
        self.pre_run_item(workflow_item, **kwargs)
        if logger.isEnabledFor(DEBUG):
            logger.debug("Calling platform_run_item")
        self.platform_run_item(workflow_item, **kwargs)
        if logger.isEnabledFor(DEBUG):
            logger.debug("Calling post_run_item")
        self.post_run_item(workflow_item, **kwargs)

    @abstractmethod
    def platform_run_item(self, workflow_item: IWorkflowItem, **kwargs):
        """
        Called during commissioning of an item. This should perform what is needed to commission job on platform.

        Args:
            workflow_item:

        Returns:
            None
        """
        pass

    @abstractmethod
    def get_parent(self, workflow_item: Any, **kwargs) -> Any:
        """
        Returns the parent of item. If the platform doesn't support parents, you should throw a TopLevelItem error.

        Args:
            workflow_item: Workflow item to get parent of
            **kwargs:

        Returns:
            Parent of Worktflow item

        Raise:
            TopLevelItem
        """
        pass

    @abstractmethod
    def get_children(self, workflow_item: Any, **kwargs) -> List[Any]:
        """
        Returns the children of an workflow_item object.

        Args:
            workflow_item: WorkflowItem object
            **kwargs: Optional arguments mainly for extensibility

        Returns:
            Children of workflow_item object
        """
        pass

    def to_entity(self, workflow_item: Any, **kwargs) -> IWorkflowItem:
        """
        Converts the platform representation of workflow_item to idmtools representation.

        Args:
            workflow_item:Platform workflow_item object

        Returns:
            IDMTools workflow_item object
        """
        return workflow_item

    @abstractmethod
    def refresh_status(self, workflow_item: IWorkflowItem, **kwargs):
        """
        Refresh status for workflow item.

        Args:
            workflow_item: Item to refresh status for

        Returns:
            None
        """
        pass

    @abstractmethod
    def send_assets(self, workflow_item: Any, **kwargs):
        """
        Send assets for workflow item to platform.

        Args:
            workflow_item: Item to send assets for

        Returns:
            None
        """
        pass

    @abstractmethod
    def get_assets(self, workflow_item: IWorkflowItem, files: List[str], **kwargs) -> Dict[str, bytearray]:
        """
        Load assets for workflow item.

        Args:
            workflow_item: Item
            files: List of files to load
            **kwargs:

        Returns:
            Dictionary with filename as key and value as binary content
        """
        pass

    @abstractmethod
    def list_assets(self, workflow_item: IWorkflowItem, **kwargs) -> List[Asset]:
        """
        List available assets for a workflow item.

        Args:
            workflow_item: workflow item to list files for

        Returns:
            List of filenames
        """
        pass
