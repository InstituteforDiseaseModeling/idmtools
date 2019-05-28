import uuid
from abc import ABCMeta

from assets.AssetCollection import AssetCollection


class IEntity(metaclass=ABCMeta):
    """
    Interface for all entities in the system.
    """

    def __init__(self, uid:uuid=None, tags:dict=None, assets=None):
        self.uid = uid
        self.tags = tags or {}
        self.assets = assets or AssetCollection()

