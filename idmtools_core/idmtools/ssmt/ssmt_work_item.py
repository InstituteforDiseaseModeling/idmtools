import typing
from dataclasses import dataclass, field
from idmtools.entities.iworkflow_item import IWorkflowItem

@dataclass
class SSMTWorkItem(IWorkflowItem):
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
class InputDataWorkItem(IWorkflowItem):
    """
    Idm InputDataWorkItem
    """

    def __post_init__(self):
        super().__post_init__()
        self.work_item_type = self.work_item_type or 'InputDataWorker'


@dataclass
class VisToolsWorkItem(IWorkflowItem):
    """
    Idm VisToolsWorkItem
    """

    def __post_init__(self):
        super().__post_init__()
        self.work_item_type = self.work_item_type or 'VisTools'


@dataclass
class GenericWorkItem(IWorkflowItem):
    """
    Idm GenericWorkItem
    """
    pass


ISSMTWorkItemClass = typing.Type[SSMTWorkItem]
IInputDataWorkItemClass = typing.Type[InputDataWorkItem]
IVisToolsWorkItemClass = typing.Type[VisToolsWorkItem]
IGenericWorkItemClass = typing.Type[GenericWorkItem]
