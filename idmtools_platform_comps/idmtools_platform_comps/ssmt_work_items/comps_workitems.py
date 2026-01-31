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

        Uses Docker Hub if use_docker_hub is True (with fallback to Artifactory).
        Otherwise uses Artifactory directly.

        Returns: final validated name
        """
        if self.docker_image:
            return self.docker_image

        if self.platform.docker_image:
            return self.platform.docker_image

        from idmtools_platform_comps.utils.package_version import (
            get_latest_ssmt_image_version,
            DOCKER_HUB_PRODUCTION,
            DOCKER_HUB_STAGING,
            GHCR_PRODUCTION,
            GHCR_STAGING
        )
        from idmtools_platform_comps import __version__

        # Determine if we're using production or staging
        is_production = "comps.idmod.org" in self.platform.endpoint.lower()

        # Get use_ghcr setting from platform (default to True)
        # Also check legacy use_docker_hub for backward compatibility
        use_ghcr = getattr(self.platform, 'use_ghcr', True)
        if not use_ghcr and hasattr(self.platform, 'use_docker_hub'):
            # Backward compatibility: if use_docker_hub is False, use GHCR
            use_ghcr = not self.platform.use_docker_hub

        # Get the version using GHCR or Docker Hub
        try:
            release = get_latest_ssmt_image_version(
                use_ghcr=use_ghcr,
                is_production=is_production,
                base_version=__version__
            )
        except ValueError as e:
            logger.error(f"Could not determine SSMT image version: {e}")
            raise

        # Build the full image path based on source
        if use_ghcr:
            # GitHub Container Registry path format (recommended)
            docker_repo = GHCR_PRODUCTION if is_production else GHCR_STAGING
            docker_image = f'{docker_repo}:{release}'
        else:
            # Docker Hub path format (legacy)
            docker_repo = DOCKER_HUB_PRODUCTION if is_production else DOCKER_HUB_STAGING
            docker_image = f'{docker_repo}:{release}'

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
