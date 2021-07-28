"""idmtools workflow item operations for ssmt.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from dataclasses import dataclass
from typing import List, Dict

from idmtools.entities.iworkflow_item import IWorkflowItem
from idmtools_platform_comps.comps_operations.workflow_item_operations import CompsPlatformWorkflowItemOperations


@dataclass
class SSMTPlatformWorkflowItemOperations(CompsPlatformWorkflowItemOperations):
    """SSMTPlatformWorkflowItemOperations provides IWorkflowItem actions for SSMT Platform.

    In IWorkflowItem's case, we just need to change how get_assets works.
    """

    def get_assets(self, workflow_item: IWorkflowItem, files: List[str], **kwargs) -> Dict[str, bytearray]:
        """
        Get Assets for workflow_item.

        Args:
            workflow_item: WorkflowItem
            files: Files to get
            **kwargs:

        Notes:
            - We need to implement this to optimize data usage on comps

        Returns:
            Files requested
        """
        raise NotImplementedError("Fetching files for WorkItem is not currently implemented for SSMT")
