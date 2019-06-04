from enum import Enum


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
