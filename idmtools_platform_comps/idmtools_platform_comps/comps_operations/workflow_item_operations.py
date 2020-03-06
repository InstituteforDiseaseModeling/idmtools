import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple, Type
from uuid import UUID

from COMPS.Data import WorkItem as COMPSWorkItem, WorkItemFile
from COMPS.Data.WorkItem import RelationType, WorkerOrPluginKey

from idmtools.assets import AssetCollection
from idmtools.core import ItemType
from idmtools.entities.generic_workitem import GenericWorkItem
from idmtools.entities.iplatform_ops.iplatform_workflowitem_operations import IPlatformWorkflowItemOperations
from idmtools.entities.iworkflow_item import IWorkflowItem
from idmtools_platform_comps.utils.general import convert_comps_workitem_status


@dataclass
class CompsPlatformWorkflowItemOperations(IPlatformWorkflowItemOperations):

    platform: 'COMPSPlaform'  # noqa F821
    platform_type: Type = field(default=COMPSWorkItem)

    def get(self, workflow_item_id: UUID, **kwargs) -> COMPSWorkItem:
        wi = COMPSWorkItem.get(workflow_item_id)
        return wi

    def platform_create(self, work_item: IWorkflowItem, **kwargs) -> Tuple[Any]:
        """
        Creates an workflow_item from an IDMTools work_item object

        Args:
            work_item: WorkflowItem to create
            **kwargs: Optional arguments mainly for extensibility

        Returns:
            Created platform item and the UUID of said item
        """
        # Collect asset files
        if not work_item.asset_collection_id:
            # Create a collection with everything that is in asset_files
            if len(work_item.asset_files.files) > 0:
                ac = AssetCollection(assets=work_item.asset_files)
                self.platform.create_items([ac])
                work_item.asset_collection_id = ac.uid

        # Create a WorkItem
        wi = COMPSWorkItem(name=work_item.item_name,
                           worker=WorkerOrPluginKey(work_item.work_item_type or self.platform.work_item_type,
                                                    work_item.plugin_key or self.platform.plugin_key),
                           environment_name=self.platform.environment,
                           asset_collection_id=work_item.asset_collection_id)

        # set tags
        wi.set_tags({})
        if work_item.tags:
            wi.set_tags(work_item.tags)

        wi.tags.update({'WorkItem_Type': work_item.work_item_type or self.platform.work_item_type})

        # Add work order file
        wo = work_item.get_base_work_order(self.platform)
        wo.update(work_item.work_order)
        wi.add_work_order(data=json.dumps(wo).encode('utf-8'))

        # Add additional files
        for af in work_item.user_files:
            wi_file = WorkItemFile(af.filename, "input")
            # Either the file has an absolute path or content
            if af.absolute_path:
                wi.add_file(wi_file, af.absolute_path)
            else:
                wi.add_file(wi_file, data=af.bytes)

        # Save the work-item to the server
        wi.save()
        wi.refresh()

        # Sets the related experiments
        if work_item.related_experiments:
            for exp_id in work_item.related_experiments:
                wi.add_related_experiment(exp_id, RelationType.DependsOn)

        # Sets the related simulations
        if work_item.related_simulations:
            for sim_id in work_item.related_simulations:
                wi.add_related_simulation(sim_id, RelationType.DependsOn)

        # Sets the related suites
        if work_item.related_suites:
            for suite_id in work_item.related_suites:
                wi.add_related_suite(suite_id, RelationType.DependsOn)

        # Sets the related work items
        if work_item.related_work_items:
            for wi_id in work_item.related_work_items:
                wi.add_related_work_item(wi_id, RelationType.DependsOn)

        # Sets the related asset collection
        if work_item.related_asset_collections:
            for ac_id in work_item.related_asset_collections:
                wi.add_related_asset_collection(ac_id, RelationType.DependsOn)

        # Set the ID back in the object
        work_item.uid = wi.id

        return work_item

    def platform_run_item(self, work_item: IWorkflowItem, **kwargs):
        """
        Start to rum COMPS WorkItem created from work_item
        Args:
            work_item: workflow item

        Returns: None
        """
        work_item.get_platform_object().commission()

    def get_parent(self, work_item: IWorkflowItem, **kwargs) -> Any:
        """
        Returns the parent of item. If the platform doesn't support parents, you should throw a TopLevelItem error
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
        Returns the children of an workflow_item object

        Args:
            work_item: WorkflowItem object
            **kwargs: Optional arguments mainly for extensibility

        Returns:
            Children of work_item object
        """
        return None

    def refresh_status(self, workflow_item: IWorkflowItem, **kwargs):
        """
                Refresh status for workflow item
                Args:
                    work_item: Item to refresh status for

                Returns:
                    None
                """
        wi = self.get(workflow_item.uid)
        workflow_item.status = convert_comps_workitem_status(wi.state)  # convert_COMPS_status(wi.state)

    def send_assets(self, workflow_item: IWorkflowItem, **kwargs):
        """
                Add asset as WorkItemFile
                Args:
                    workflow_item: workflow item

                Returns: None
                """
        # for asset in workflow_item.assets:
        #     workflow_item.add_file(workitemfile=WorkItemFile(asset.filename, 'input'), data=asset.bytes)
        pass

    def list_assets(self, workflow_item: IWorkflowItem, **kwargs) -> List[str]:
        """
        Get list of asset files
        Args:
            workflow_item: workflow item
            **kwargs: Optional arguments mainly for extensibility

        Returns: list of assets associated with WorkItem

        """
        # item: IWorkflowItem = workflow_item.get_platform_object(True)
        # return item.files
        pass

    def get_assets(self, workflow_item: IWorkflowItem, files: List[str], **kwargs) -> Dict[str, bytearray]:
        """
        Retrieve files association with WorkItem
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
        Converts the platform representation of workflow_item to idmtools representation

        Args:
            work_item:Platform workflow_item object
            **kwargs: Optional arguments mainly for extensibility

        Returns:
            IDMTools workflow item
                """
        # Creat a workflow item
        obj = GenericWorkItem()

        # Set its correct attributes
        obj.item_name = work_item.name
        obj.platform = self.platform
        obj.uid = work_item.id
        obj.asset_collection_id = work_item.asset_collection_id
        obj.user_files = work_item.files
        obj.tags = work_item.tags
        return obj

    # def platform_run_item(self, workflow_item: IWorkflowItem, **kwargs):
    #     raise NotImplementedError("Running workflow items is not supported")

    def get_related_items(self, item: IWorkflowItem, relation_type: RelationType) -> Dict[str, List[Dict[str, str]]]:
        """
        Get related WorkItems, Suites, Experiments, Simulations and AssetCollections
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
