from dataclasses import field, dataclass
from typing import List, Dict, Any, Tuple, Type
from uuid import UUID
from idmtools.assets import Asset
from idmtools.entities.iplatform_ops.iplatform_workflowitem_operations import IPlatformWorkflowItemOperations
from idmtools.entities.iworkflow_item import IWorkflowItem


# Class to distinguish between regular AC and our platform and for type mapping on the platform
class FilePlatformIWorkflowItem(IWorkflowItem):
    pass


@dataclass
class FilePlatformWorkflowItemOperations(IPlatformWorkflowItemOperations):
    platform: 'FilePlatform'  # noqa F821
    platform_type: Type = field(default=FilePlatformIWorkflowItem)

    def get(self, workflow_item_id: UUID, **kwargs) -> Any:
        pass

    def platform_create(self, workflow_item: IWorkflowItem, **kwargs) -> Tuple[Any, UUID]:
        pass

    def platform_run_item(self, workflow_item: IWorkflowItem, **kwargs):
        pass

    def get_parent(self, workflow_item: Any, **kwargs) -> Any:
        pass

    def get_children(self, workflow_item: Any, **kwargs) -> List[Any]:
        pass

    def refresh_status(self, workflow_item: IWorkflowItem, **kwargs):
        pass

    def send_assets(self, workflow_item: Any, **kwargs):
        pass

    def get_assets(self, workflow_item: IWorkflowItem, files: List[str], **kwargs) -> Dict[str, bytearray]:
        pass

    def list_assets(self, workflow_item: IWorkflowItem, **kwargs) -> List[Asset]:
        pass
