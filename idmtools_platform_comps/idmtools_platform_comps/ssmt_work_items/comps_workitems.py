"""idmtools SSMTWorkItem. This is the base of most comps workitems.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from logging import getLogger, DEBUG
from dataclasses import dataclass, field, InitVar
from uuid import UUID
from idmtools.assets.file_list import FileList
from idmtools.entities.command_task import CommandTask
from idmtools_platform_comps.ssmt_work_items.icomps_workflowitem import ICOMPSWorkflowItem

logger = getLogger(__name__)
user_logger = getLogger(__name__)


@dataclass
class SSMTWorkItem(ICOMPSWorkflowItem):
    """
    Defines the SSMT WorkItem.

    Notes:
        - We have lots of workitem bases. We need to consolidate these a bit.
    """
    docker_image: str = field(default=None)
    command: InitVar[str] = None

    def __post_init__(self, item_name: str, asset_collection_id: UUID, asset_files: FileList, user_files: FileList, command: str):
        """Constructor."""
        if command and not self.task:
            self.task = CommandTask(command)
        else:
            user_logger.warning("You provided both a task and a command. Only using the task")
        super().__post_init__(item_name, asset_collection_id, asset_files, user_files)

        self.work_item_type = self.work_item_type or 'DockerWorker'

    def get_base_work_order(self):
        """
        Builder basic work order.

        Returns: work order as a dictionary
        """
        base_wo = {
            "WorkItem_Type": self.work_item_type,
            "Execution": {
                "ImageName": self.get_comps_ssmt_image_name(),
                "Command": str(self.task.command)
            }
        }

        return base_wo

    def get_comps_ssmt_image_name(self):
        """
        Build comps ssmt docker image name.

        Returns: final validated name
        """
        if self.docker_image:
            return self.docker_image

        if self.platform.docker_image:
            return self.platform.docker_image

        SSMT_PRODUCTION_IMAGE = 'docker-production.packages.idmod.org/idmtools/comps_ssmt_worker'
        SSMT_STAGING_IMAGE = 'docker-staging.packages.idmod.org/idmtools/comps_ssmt_worker'

        from idmtools_platform_comps.utils.package_version import get_latest_ssmt_image_version_from_artifactory
        from idmtools_platform_comps import __version__

        # Determine the default ssmt docker image
        if "comps.idmod.org" in self.platform.endpoint.lower():
            ssmt_image = SSMT_PRODUCTION_IMAGE
        else:
            ssmt_image = SSMT_STAGING_IMAGE

        release = get_latest_ssmt_image_version_from_artifactory(base_version=__version__)

        docker_image = f'{ssmt_image}:{release}'
        if logger.isEnabledFor(DEBUG):
            logger.debug(f'docker_image in use: {docker_image}')

        return docker_image


@dataclass
class InputDataWorkItem(ICOMPSWorkflowItem):
    """
    Idm InputDataWorkItem.

    Notes:
        - TODO add examples
    """

    def __post_init__(self, item_name: str, asset_collection_id: UUID, asset_files: FileList, user_files: FileList):
        """Constructor."""
        super().__post_init__(item_name, asset_collection_id, asset_files, user_files)
        self.work_item_type = self.work_item_type or 'InputDataWorker'


@dataclass
class VisToolsWorkItem(ICOMPSWorkflowItem):
    """
    Idm VisToolsWorkItem.

    Notes:
        - TODO add examples
    """

    def __post_init__(self, item_name: str, asset_collection_id: UUID, asset_files: FileList, user_files: FileList):
        """Constructor."""
        super().__post_init__(item_name, asset_collection_id, asset_files, user_files)
        self.work_item_type = self.work_item_type or 'VisTools'
