import json

from COMPS.Data import WorkItemFile
from dataclasses import dataclass, field

from idmtools.assets import AssetCollection
from idmtools.entities.iplatform_metadata import IPlatformWorkItemOperations
from COMPS.Data.WorkItem import WorkItem as COMPSWorkItem, WorkItem, WorkerOrPluginKey, RelationType
from idmtools.entities.iwork_item import IWorkItem
from typing import Any, List, Tuple, Type, Dict
from uuid import UUID


@dataclass
class SSMTPlatformWorkItemOperations(IPlatformWorkItemOperations):
    platform: 'COMPSPlaform'  # noqa F821
    platform_type: Type = field(default=COMPSWorkItem)

    def get(self, work_item_id: UUID, **kwargs) -> Any:
        """
        Returns the platform representation of an WorkItem

        Args:
            work_item_id: Item id of WorkItems
            **kwargs:

        Returns:
            Platform Representation of an work_item
        """
        wi = WorkItem.get(work_item_id)
        return wi

    def batch_create(self, work_items: List[IWorkItem], **kwargs) -> List[Tuple[Any, UUID]]:
        """
        Provides a method to batch create workflow items

        Args:
            workflow_items: List of work items to create
            **kwargs:

        Returns:
            List of tuples containing the create object and id of item that was created
        """
        ret = []
        for wi in work_items:
            ret.append(self.create(wi, **kwargs))
        return ret

    def create(self, work_item: IWorkItem, **kwargs) -> Tuple[Any, UUID]:
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
                ac = AssetCollection(local_files=work_item.asset_files)
                ac.prepare("HPC")
                work_item.asset_collection_id = ac.collection_id

        # Create a WorkItem
        wi = WorkItem(name=work_item.item_name,
                      worker=WorkerOrPluginKey(self.platform.item_type, self.platform.plugin_key),
                      environment_name=self.platform.environment, asset_collection_id=work_item.asset_collection_id)

        # set tags
        if work_item.tags:
            wi.set_tags(work_item.tags)

        # Add work order file
        wo = {
            "WorkItem_Type": self.platform.item_type,
            "Execution": {
                "ImageName": self.platform.docker_image,
                "Command": work_item.command
            }
        }
        wo.update(work_item.wo_kwargs)
        wi.add_work_order(data=json.dumps(wo).encode('utf-8'))

        # Add additional files
        for af in work_item.user_files:
            wi_file = WorkItemFile(af.filename, "input")
            wi.add_file(wi_file, af.absolute_path)

        # Save the work-item to the server
        wi.save()
        wi.refresh()

        # Sets the related experiments
        if work_item.related_experiments:
            for exp_id in work_item.related_experiments:
                wi.add_related_experiment(exp_id, RelationType.DependsOn)

        # Set the ID back in the object
        work_item.uid = wi.id

        return work_item, wi.id

    def run_item(self, work_item: IWorkItem):
        work_item.get_platform_object().commission()

    def refresh_status(self, work_item: IWorkItem):
        """
        Refresh status for workflow item
        Args:
            work_item: Item to refresh status for

        Returns:
            None
        """
        wi = self.get(work_item.uid)
        work_item.status = wi.state   # convert_COMPS_status(wi.state)

    def get_parent(self, work_item: Any, **kwargs) -> Any:
        """
        Returns the parent of item. If the platform doesn't support parents, you should throw a TopLevelItem error

        Args:
            work_item:
            **kwargs:

        Returns:

        Raise:
            TopLevelItem
        """
        pass

    def get_children(self, work_item: Any, **kwargs) -> List[Any]:
        """
        Returns the children of an workflow_item object

        Args:
            work_item: WorkflowItem object
            **kwargs: Optional arguments mainly for extensibility

        Returns:
            Children of work_item object
        """
        pass

    def to_entity(self, work_item: Any, **kwargs) -> IWorkItem:
        """
        Converts the platform representation of workflow_item to idmtools representation

        Args:
            work_item:Platform workflow_item object

        Returns:
            IDMTools workflow_item object
        """
        return work_item

    def get_assets(self, work_item: IWorkItem, files: List[str], **kwargs) -> Dict[str, bytearray]:
        """
        Load assets for workflow item
        Args:
            workflow_item: Item
            files: List of files to load
            **kwargs:

        Returns:
            Dictionary with filename as key and value as binary content
        """
        raise NotImplementedError("Fetching files for simulation is not currently implemented for SSMT")


    def send_assets(self, work_item: Any):
        """
        Send assets for workflow item to platform

        Args:
            work_item: Item to send assets for

        Returns:

        """
        pass

    def list_assets(self, work_item: IWorkItem) -> List[str]:
        """
        List files available  for workflow item

        Args:
            work_item: Workflow item

        Returns:
            List of filenames
        """
        pass
