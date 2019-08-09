from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field

from idmtools.core import EntityStatus
from idmtools.core.interfaces.IEntity import IEntity
from idmtools.core.item_id import ItemId


@dataclass
class IItem(IEntity, metaclass=ABCMeta):
    """
    A generic thing that can be run and have a status.
    """
    status: 'EntityStatus' = field(default=None, compare=False)
    full_id: ItemId = field(default=None, metadata={"md": True})

    @property
    def done(self):
        return self.status in (EntityStatus.SUCCEEDED, EntityStatus.FAILED)

    @property
    def succeeded(self):
        return self.status == EntityStatus.SUCCEEDED
