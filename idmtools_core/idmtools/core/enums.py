from enum import Enum, auto


class EntityStatus(Enum):
    CREATED = 'created'
    RUNNING = 'running'
    SUCCEEDED = 'succeeded'
    FAILED = 'failed'
    CANCELED = 'canceled'


class FilterMode(Enum):
    """
    Allows user to specify AND/OR for the filtering system.
    """
    AND = 0
    OR = 1


class ItemType(Enum):
    SUITE = auto()
    EXPERIMENT = auto()
    SIMULATION = auto()
    WORKITEM = auto()
    ASSETCOLLECTION = auto()
