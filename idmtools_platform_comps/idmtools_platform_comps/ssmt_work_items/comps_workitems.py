from dataclasses import dataclass, field
from idmtools_platform_comps.ssmt_work_items.icomps_workflowitem import ICOMPSWorkflowItem


@dataclass
class SSMTWorkItem(ICOMPSWorkflowItem):
    """
    Idm SSMTWorkItem
    """
    docker_image: str = field(default=None)
    command: str = field(default=None)

    def __post_init__(self):
        super().__post_init__()
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

        from idmtools_platform_comps import __version__
        from idmtools_platform_comps.utils.package_version import get_latest_ssmt_image_version_from_artifactory

        # Determine the default ssmt docker image
        if "comps.idmod.org" in self.platform.endpoint.lower():
            ssmt_image = SSMT_PRODUCTION_IMAGE
        else:
            ssmt_image = SSMT_STAGING_IMAGE

        release = get_latest_ssmt_image_version_from_artifactory()
        return f'{ssmt_image}:{release}'


@dataclass
class InputDataWorkItem(ICOMPSWorkflowItem):
    """
    Idm InputDataWorkItem
    """

    def __post_init__(self):
        super().__post_init__()
        self.work_item_type = self.work_item_type or 'InputDataWorker'


@dataclass
class VisToolsWorkItem(ICOMPSWorkflowItem):
    """
    Idm VisToolsWorkItem
    """

    def __post_init__(self):
        super().__post_init__()
        self.work_item_type = self.work_item_type or 'VisTools'
