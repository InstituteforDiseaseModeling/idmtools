from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple, Type
from uuid import UUID

from COMPS.Data import WorkItem, QueryCriteria, WorkItemFile

from idmtools.entities.iplatform_ops.iplatform_workflowitem_operations import IPlatformWorkflowItemOperations
from idmtools.entities.iworkflow_item import IWorkflowItem
from idmtools_platform_comps.utils.general import convert_COMPS_status, get_asset_for_comps_item


@dataclass
class CompsPlatformWorkflowItemOperations(IPlatformWorkflowItemOperations):

    platform: 'COMPSPlaform'  # noqa F821
    platform_type: Type = field(default=WorkItem)

    def get(self, workflow_item_id: UUID, **kwargs) -> WorkItem:
        cols = kwargs.get('columns')
        children = kwargs.get('children')
        cols = cols or ["id", "name", "suite_id"]
        children = children if children is not None else ["tags", "configuration"]
        return WorkItem.get(id=workflow_item_id, query_criteria=QueryCriteria().select(cols).select_children(children))

    def platform_create(self, workflow_item: IWorkflowItem, **kwargs) -> Tuple[Any, UUID]:
        raise NotImplementedError("Creating workflow items is not supported")

    def get_parent(self, workflow_item: WorkItem, **kwargs) -> Any:
        return None

    def get_children(self, workflow_item: WorkItem, **kwargs) -> List[Any]:
        raise NotImplementedError("Getting Children is not yet supported for WorkItems")

    def refresh_status(self, workflow_item: IWorkflowItem, **kwargs):
        s = WorkItem.get(id=workflow_item.uid, query_criteria=QueryCriteria().select(['state']))
        workflow_item.status = convert_COMPS_status(s.state)
        # TODO get children status possibly?

    def send_assets(self, workflow_item: WorkItem, **kwargs):
        for asset in workflow_item.assets:
            workflow_item.add_file(workitemfile=WorkItemFile(asset.filename, 'input'), data=asset.bytes)

    def list_assets(self, workflow_item: IWorkflowItem, **kwargs) -> List[str]:
        item: WorkItem = workflow_item.get_platform_object(True, children=["files", "configuration"])
        return item.files

    def get_assets(self, workflow_item: IWorkflowItem, files: List[str], **kwargs) -> Dict[str, bytearray]:
        return get_asset_for_comps_item(self.platform, workflow_item, files, self.cache)

    def to_entity(self, workflow_item: Any, **kwargs) -> IWorkflowItem:
        raise NotImplementedError("Converting workitems to platform entities is not yet supported")

    def platform_run_item(self, workflow_item: IWorkflowItem, **kwargs):
        raise NotImplementedError("Running workflow items is not supported")
