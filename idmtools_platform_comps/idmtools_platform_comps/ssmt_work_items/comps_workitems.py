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

    def get_base_work_order(self, platform):
        wi_type = self.work_item_type or platform.work_item_type

        base_wo = {
            "WorkItem_Type": wi_type,
            "Execution": {
                "ImageName": self.docker_image or platform.docker_image,
                "Command": self.command
            }
        }

        return base_wo


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
