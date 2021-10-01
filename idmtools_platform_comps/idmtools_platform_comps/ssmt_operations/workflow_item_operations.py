"""idmtools workflow item operations for ssmt.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import os
from dataclasses import dataclass
from uuid import UUID
from typing import List, Dict, Optional
from idmtools.entities.iworkflow_item import IWorkflowItem
from idmtools_platform_comps.comps_operations.workflow_item_operations import CompsPlatformWorkflowItemOperations
from COMPS.Data.WorkItem import WorkItem as COMPSWorkItem
from COMPS.Data import QueryCriteria
from logging import getLogger, DEBUG

logger = getLogger(__name__)


@dataclass
class SSMTPlatformWorkflowItemOperations(CompsPlatformWorkflowItemOperations):
    """SSMTPlatformWorkflowItemOperations provides IWorkflowItem actions for SSMT Platform.

    In IWorkflowItem's case, we just need to change how get_assets works.
    """

    def get(self, workflow_item_id: UUID, columns: Optional[List[str]] = None, load_children: Optional[List[str]] = None,
            query_criteria: Optional[QueryCriteria] = None, **kwargs) -> \
            COMPSWorkItem:
        """
        Get COMPSWorkItem.

        Args:
            workflow_item_id: Item id
            columns: Optional columns to load. Defaults to "id", "name", "state", "environment_name", "working_directory"
            load_children: Optional list of COMPS Children objects to load. Defaults to "Tags"
            query_criteria: Optional QueryCriteria
            **kwargs:

        Returns:
            COMPSWorkItem
        """
        columns = columns or ["id", "name", "state", "environment_name", "working_directory"]
        if "working_directory" not in columns:
            columns.append("working_directory")

        return super().get(workflow_item_id, columns=columns, load_children=load_children, query_criteria=query_criteria)

    def get_assets(self, workflow_item: IWorkflowItem, files: List[str], **kwargs) -> Dict[str, bytearray]:
        """
        Get Assets for workflow_item.

        Args:
            workflow_item: WorkflowItem
            files: Files to get
            **kwargs:

        Returns:
            Files requested
        """
        files = [f.replace("\\", '/') for f in files]
        po: COMPSWorkItem = workflow_item.get_platform_object()
        working_directory = po.working_directory
        results = dict()
        for file in files:
            full_path = os.path.join(working_directory, file)
            full_path = full_path.replace("\\", '/')
            if not os.path.exists(full_path):
                msg = f"Cannot find the file {file} at {full_path}"
                logger.error(msg)
                raise FileNotFoundError(msg)
            if logger.isEnabledFor(DEBUG):
                logger.debug(full_path)
            with open(full_path, 'rb') as fin:
                results[file] = fin.read()
        return results
