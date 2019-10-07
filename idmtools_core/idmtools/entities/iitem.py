from abc import ABCMeta
from dataclasses import dataclass, field
from idmtools.core import EntityStatus
from idmtools.core.interfaces.ientity import IEntity

import typing
if typing.TYPE_CHECKING:
    from idmtools.core.enums import EntityStatus


@dataclass(repr=False)
class IItem(IEntity, metaclass=ABCMeta):
    """
    A generic thing that can be run and have a status.
    """
    status: 'EntityStatus' = field(default=None, compare=False)

    @property
    def done(self) -> bool:
        return self.status in (EntityStatus.SUCCEEDED, EntityStatus.FAILED)

    @property
    def succeeded(self) -> bool:
        return self.status == EntityStatus.SUCCEEDED


TItem = typing.TypeVar("TItem", bound=IItem)
TItemList = typing.List[TItem]
