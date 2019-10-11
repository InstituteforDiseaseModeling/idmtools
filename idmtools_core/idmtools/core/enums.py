from enum import Enum, auto


class EntityStatus(Enum):
    CREATED = 'created'
    RUNNING = 'running'
    SUCCEEDED = 'succeeded'
    FAILED = 'failed'


class FilterMode(Enum):
    """
    Allows to specify AND/OR for the filtering system
    """
    AND = 0
    OR = 1


class ObjectType(Enum):
    SUITE = auto()
    EXPERIMENT = auto()
    SIMULATION = auto()
    WORKITEM = auto()
    ASSETCOLLECTION = auto()
