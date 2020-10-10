import warnings
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
    Idm SSMTWorkItem
    """
    docker_image: str = field(default=None)
    command: InitVar[str] = None

    def __post_init__(self, item_name: str, asset_collection_id: UUID, asset_files: FileList, user_files: FileList, command: str):
        super().__post_init__(item_name, asset_collection_id, asset_files, user_files)
        if command and not self.task:
            self.task = CommandTask(command)
        else:
            user_logger.warning("You provided both a task and a command. Only using the task")
        self.work_item_type = self.work_item_type or 'DockerWorker'

    def get_base_work_order(self):
        """
        builder basic work order
        Returns: work order as a dictionary
        """
        base_wo = {
            "WorkItem_Type": self.work_item_type,
            "Execution": {
                "ImageName": self.get_comps_ssmt_image_name(),
                "Command": self.command
            }
        }

        return base_wo

    def get_comps_ssmt_image_name(self):
        """
        build comps ssmt docker image name
        Args:
            user_image: the image name provided by user

        Returns: final validated name
        """
        if self.docker_image:
            return self.docker_image

        if self.platform.docker_image:
            return self.platform.docker_image

        SSMT_PRODUCTION_IMAGE = 'docker-production.packages.idmod.org/idmtools/comps_ssmt_worker'
        SSMT_STAGING_IMAGE = 'docker-staging.packages.idmod.org/idmtools/comps_ssmt_worker'

        from idmtools_platform_comps.utils.package_version import get_latest_ssmt_image_version_from_artifactory

        # Determine the default ssmt docker image
        if "comps.idmod.org" in self.platform.endpoint.lower():
            ssmt_image = SSMT_PRODUCTION_IMAGE
        else:
            ssmt_image = SSMT_STAGING_IMAGE

        release = get_latest_ssmt_image_version_from_artifactory()

        docker_image = f'{ssmt_image}:{release}'
        if logger.isEnabledFor(DEBUG):
            logger.debug(f'docker_image in use: {docker_image}')

        return docker_image

    @property
    def command(self) -> str:
        return self.task.command

    @command.setter
    def command(self, value: str):
        """
        Alias for legacy code for assets. It will be deprecated in 1.7.0

        Returns:
            None
        """
        warnings.warn("Setting commands via command alias will be deprecated in 1.7.0. Set on task, task.command", DeprecationWarning)
        self.task.command = value


@dataclass
class InputDataWorkItem(ICOMPSWorkflowItem):
    """
    Idm InputDataWorkItem
    """

    def __post_init__(self, item_name: str, asset_collection_id: UUID, asset_files: FileList, user_files: FileList):
        super().__post_init__(item_name, asset_collection_id, asset_files, user_files)
        self.work_item_type = self.work_item_type or 'InputDataWorker'


@dataclass
class VisToolsWorkItem(ICOMPSWorkflowItem):
    """
    Idm VisToolsWorkItem
    """

    def __post_init__(self, item_name: str, asset_collection_id: UUID, asset_files: FileList, user_files: FileList):
        super().__post_init__(item_name, asset_collection_id, asset_files, user_files)
        self.work_item_type = self.work_item_type or 'VisTools'
