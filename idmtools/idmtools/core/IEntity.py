import uuid
from abc import ABCMeta


class IEntity(metaclass=ABCMeta):
    """
    Interface for all entities in the system.
    """

    def __init__(self, uid: uuid = None, tags: dict = None):
        self.uid = uid
        self.tags = tags or {}
