from dataclasses import dataclass

from idmtools.entities.iworkflow_item import IWorkflowItem


@dataclass
class GenericWorkItem(IWorkflowItem):
    """
    Idm GenericWorkItem
    """
    def __hash__(self):
        return hash(self.id)
