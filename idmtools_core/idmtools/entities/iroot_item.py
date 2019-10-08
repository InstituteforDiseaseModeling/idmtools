import uuid
from abc import ABCMeta
from idmtools.entities.iitem import TItemList, IItem, TItem
from dataclasses import dataclass, field
# ck4, replace EntityContainer with this, I think
from idmtools.entities.iplatform import TPlatform


@dataclass(repr=False)
class IRootItem(IItem, metaclass=ABCMeta):
    """
    An object that is both an item AND can contain (be a parent of) other _items
    """

    class NoPlatformException(Exception):
        pass

    class FamilyException(Exception):
        pass

    parent_id: uuid = field(default=None, compare=False)
    children_ids: TItemList = field(default=None, compare=False)
    _parent: TItem = field(default=None)
    _children: TItemList = field(default=None)
    platform: TPlatform = field(default=None)

    def parent(self, refresh: bool = False, full_load: bool = False) -> TItemList:  # noqa: F841
        if self.platform is not None:
            if self._parent is None or refresh:
                self._parent = self.platform.get_parent(self)  # TODO implement full_load, full_load=full_load)
        else:
            raise self.NoPlatformException('Items require a platform object to resolve their parent_id to an object.')
        return self._parent

    def children(self, refresh: bool = False, full_load: bool = False) -> TItemList:  # noqa: F841
        return None
