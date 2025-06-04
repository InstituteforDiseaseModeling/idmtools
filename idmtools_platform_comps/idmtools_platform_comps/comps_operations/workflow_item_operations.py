"""idmtools comps workflow item operations.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import json
import typing
from dataclasses import dataclass, field
from logging import getLogger, DEBUG
from typing import Any, Dict, List, Tuple, Type, Optional
from uuid import UUID
from COMPS.Data import QueryCriteria, WorkItem as COMPSWorkItem, WorkItemFile
from COMPS.Data.WorkItem import RelationType, WorkerOrPluginKey
from idmtools import IdmConfigParser
from idmtools.assets import AssetCollection
from idmtools.core import ItemType
from idmtools.core.interfaces.ientity import IEntity
from idmtools.entities.generic_workitem import GenericWorkItem
from idmtools.entities.iplatform_ops.iplatform_workflowitem_operations import IPlatformWorkflowItemOperations
from idmtools.entities.iworkflow_item import IWorkflowItem
from idmtools_platform_comps.utils.general import convert_comps_workitem_status

if typing.TYPE_CHECKING:
    from idmtools_platform_comps.comps_platform import COMPSPlatform

logger = getLogger(__name__)
user_logger = getLogger('user')


@dataclass
class CompsPlatformWorkflowItemOperations(IPlatformWorkflowItemOperations):
    """Provides IWorkflowItem COMPSPlatform."""
    platform: 'COMPSPlatform'  # noqa F821
    platform_type: Type = field(default=COMPSWorkItem)

    def get(self, workflow_item_id: UUID, columns: Optional[List[str]] = None, load_children: Optional[List[str]] = None,
            query_criteria: Optional[QueryCriteria] = None, **kwargs) -> \
            COMPSWorkItem:
        """
        Get COMPSWorkItem.

        Args:
            workflow_item_id: Item id
            columns: Optional columns to load. Defaults to "id", "name", "state"
            load_children: Optional list of COMPS Children objects to load. Defaults to "Tags"
            query_criteria: Optional QueryCriteria
            **kwargs:

        Returns:
            COMPSWorkItem
        """
        columns = columns or ["id", "name", "state", "environment_name"]
        load_children = load_children if load_children is not None else ["tags"]
        query_criteria = query_criteria or QueryCriteria().select(columns).select_children(load_children)
        return COMPSWorkItem.get(workflow_item_id, query_criteria=query_criteria)

    def platform_create(self, work_item: IWorkflowItem, **kwargs) -> Tuple[Any]:
        """
        Creates an workflow_item from an IDMTools work_item object.

        Args:
            work_item: WorkflowItem to create
            **kwargs: Optional arguments mainly for extensibility

        Returns:
            Created platform item and the UUID of said item
        """
        self.send_assets(work_item)

        if logger.isEnabledFor(DEBUG):
            logger.debug(f"Creating workitem {work_item.name} of type {work_item.work_item_type}, "
                         f"{work_item.plugin_key} in {self.platform.environment}")
        # Create a WorkItem
        wi = COMPSWorkItem(name=work_item.name,
                           worker=WorkerOrPluginKey(work_item.work_item_type, work_item.plugin_key),
                           environment_name=self.platform.environment,
                           asset_collection_id=work_item.assets.id if len(work_item.assets) else None)

        # Set tags
        wi.set_tags({})
        if work_item.tags:
            wi.set_tags(work_item.tags)

        # Update tags
        wi.tags.update({'WorkItem_Type': work_item.work_item_type})

        # Add work order file
        wo = work_item.get_base_work_order()
        wo.update(work_item.work_order)
        wi.add_work_order(data=json.dumps(wo).encode('utf-8'))

        # Add additional files
        for af in work_item.transient_assets:
            wi_file = WorkItemFile(af.filename, "input")
            # Either the file has an absolute path or content
            if af.absolute_path:
                wi.add_file(wi_file, af.absolute_path)
            else:
                wi.add_file(wi_file, data=af.bytes)

        if logger.isEnabledFor(DEBUG):
            logger.debug("Sending workitem to COMPS")
        # Save the work-item to the server
        wi.save()
        wi.refresh()

        if logger.isEnabledFor(DEBUG):
            logger.debug("Set the relationships")

        # Ensure any items that are objects are converted to ids
        for attr_name in ['related_experiments', 'related_simulations', 'related_work_items', 'related_asset_collections']:
            if getattr(work_item, attr_name):
                for item in getattr(work_item, attr_name):
                    getattr(wi, f'add_{attr_name[:-1]}')(item.id if isinstance(item, IEntity) else item, RelationType.DependsOn)

        wi.save()

        # Set the ID back in the object
        work_item.uid = wi.id

        return work_item

    def platform_run_item(self, work_item: IWorkflowItem, **kwargs):
        """
        Start to rum COMPS WorkItem created from work_item.

        Args:
            work_item: workflow item

        Returns: None
        """
        work_item.get_platform_object().commission()
        if IdmConfigParser.is_output_enabled():
            user_logger.info(
                f"\nThe running WorkItem can be viewed at {self.platform.get_workitem_link(work_item)}\n"
            )

    def get_parent(self, work_item: IWorkflowItem, **kwargs) -> Any:
        """
        Returns the parent of item. If the platform doesn't support parents, you should throw a TopLevelItem error.

        Args:
            work_item: COMPS WorkItem
            **kwargs: Optional arguments mainly for extensibility

        Returns: item parent

        Raise:
            TopLevelItem
        """
        return None

    def get_children(self, work_item: IWorkflowItem, **kwargs) -> List[Any]:
        """
        Returns the children of an workflow_item object.

        Args:
            work_item: WorkflowItem object
            **kwargs: Optional arguments mainly for extensibility

        Returns:
            Children of work_item object
        """
        return None

    def refresh_status(self, workflow_item: IWorkflowItem, **kwargs):
        """
        Refresh status for workflow item.

        Args:
            work_item: Item to refresh status for

        Returns:
            None
        """
        wi = self.get(workflow_item.uid, columns=["id", "state"], load_children=[])
        workflow_item.status = convert_comps_workitem_status(wi.state)  # convert_COMPS_status(wi.state)

    def send_assets(self, workflow_item: IWorkflowItem, **kwargs):
        """
        Add asset as WorkItemFile.

        Args:
            workflow_item: workflow item

        Returns: None
        """
        # Collect asset files
        if workflow_item.assets and len(workflow_item.assets):
            if logger.isEnabledFor(DEBUG):
                logger.debug("Uploading assets for Workitem")
            self.platform._assets.create(workflow_item.assets)

    def list_assets(self, workflow_item: IWorkflowItem, **kwargs) -> List[str]:
        """
        Get list of asset files.

        Args:
            workflow_item: workflow item
            **kwargs: Optional arguments mainly for extensibility

        Returns: list of assets associated with WorkItem
        """
        wi: COMPSWorkItem = workflow_item.get_platform_object()
        return wi.files

    def get_assets(self, workflow_item: IWorkflowItem, files: List[str], **kwargs) -> Dict[str, bytearray]:
        """
        Retrieve files association with WorkItem.

        Args:
            workflow_item: workflow item
            files: list of file paths
            **kwargs: Optional arguments mainly for extensibility

        Returns: dict with key/value: file_path/file_content
        """
        wi = self.platform.get_item(workflow_item.uid, ItemType.WORKFLOW_ITEM, raw=True)
        byte_arrs = wi.retrieve_output_files(files)
        return dict(zip(files, byte_arrs))

    def to_entity(self, work_item: COMPSWorkItem, **kwargs) -> IWorkflowItem:
        """
        Converts the platform representation of workflow_item to idmtools representation.

        Args:
            work_item:Platform workflow_item object
            kwargs: optional arguments mainly for extensibility

        Returns:
            IDMTools workflow item
        """
        # Creat a workflow item
        # Eventually it would be nice to put the actual command here, but this requires fetching the work-order which is a bit to much overhead
        obj = GenericWorkItem(name=work_item.name, command="")

        # Set its correct attributes
        obj.platform = self.platform
        obj._platform_object = work_item
        obj.uid = work_item.id
        if work_item.asset_collection_id:
            obj.assets = AssetCollection.from_id(work_item.asset_collection_id, platform=self.platform)
        if work_item.files:
            obj.transient_assets = self.platform._assets.to_entity(work_item.files)
        obj.tags = work_item.tags
        obj.status = convert_comps_workitem_status(work_item.state)
        return obj

    # def platform_run_item(self, workflow_item: IWorkflowItem, **kwargs):
    #     raise NotImplementedError("Running workflow items is not supported")

    def get_related_items(self, item: IWorkflowItem, relation_type: RelationType) -> Dict[str, List[Dict[str, str]]]:
        """
        Get related WorkItems, Suites, Experiments, Simulations and AssetCollections.

        Args:
            item: workflow item
            relation_type: RelationType

        Returns: Dict
        """
        wi = self.platform.get_item(item.uid, ItemType.WORKFLOW_ITEM, raw=True)

        ret = {}
        ret['work_item'] = wi.get_related_work_items(relation_type)
        ret['suite'] = wi.get_related_suites(relation_type)
        ret['experiment'] = wi.get_related_experiments(relation_type)
        ret['simulation'] = wi.get_related_simulations(relation_type)
        ret['asset_collection'] = wi.get_related_asset_collections(relation_type)

        return ret
