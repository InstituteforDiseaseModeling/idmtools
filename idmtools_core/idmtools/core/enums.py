from enum import Enum

TRUTHY_VALUES = ['1', 'y', 'yes', 'on', 'true', 't']


class EntityStatus(Enum):
    COMMISSIONING = 'commissioning'
    CREATED = 'created'
    RUNNING = 'running'
    SUCCEEDED = 'succeeded'
    FAILED = 'failed'


class FilterMode(Enum):
    """
    Allows user to specify AND/OR for the filtering system.
    """
    AND = 0
    OR = 1


class ItemType(Enum):
    SUITE = "Suite"
    EXPERIMENT = "Experiment"
    SIMULATION = "Simulation"
    WORKFLOW_ITEM = "WorkItem"  # On Comps this is workitems
    ASSETCOLLECTION = "Asset Collection"

    def __str__(self):
        return str(self.value)
