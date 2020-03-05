import json
from abc import ABC

from dataclasses import field, dataclass

from idmtools.entities.iworkflow_item import IWorkflowItem


@dataclass
class ICOMPSWorkflowItem(IWorkflowItem, ABC):
    """
    Interface of idmtools work item
    """

    item_name: str = field(default="Idm WorkItem Test")
    work_order: dict = field(default_factory=lambda: {})
    work_item_type: str = field(default=None)
    plugin_key: str = field(default="1.0.0.0_RELEASE")

    def __post_init__(self):
        super().__post_init__()
        self.work_order = self.work_order or {}

    def __repr__(self):
        return f"<WorkItem {self.uid}>"

    def get_base_work_order(self, platform):
        wi_type = self.work_item_type or platform.work_item_type
        base_wo = {"WorkItem_Type": wi_type}
        return base_wo

    def load_work_order(self, wo_file):
        self.work_order = json.load(open(wo_file, 'rb'))

    def set_work_order(self, wo):
        """
        Update wo for the name with value
        Args:
            wo: user wo
        Returns: None
        """
        self.work_order = wo

    def update_work_order(self, name, value):
        """
        Update wo for the name with value
        Args:
            name: wo arg name
            value: wo arg value

        Returns: None
        """
        self.work_order[name] = value

    def clear_wo_args(self):
        """
        Clear all existing wo args

        Returns: None

        """
        self.work_order = {}
