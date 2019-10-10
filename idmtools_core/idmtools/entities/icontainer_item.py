import uuid
from abc import ABCMeta
from idmtools.entities.iitem import IItem, TItemList, TItem
from idmtools.core.interfaces.entity_container import EntityContainer
from dataclasses import dataclass, field
from idmtools.entities.iplatform import TPlatform


@dataclass(repr=False)
class IContainerItem(IItem, metaclass=ABCMeta):
    """
    An object that is both an item AND can contain (be a parent of) other _items
    """

    class NoPlatformException(Exception):
        pass

    parent_id: uuid = field(default=None, compare=False)
    children_ids: TItemList = field(default=None, compare=False)
    _parent: TItem = field(default=None)
    _children: TItemList = field(default=None)
    platform: TPlatform = field(default=None)

    def parent(self, platform: 'TPlatform' = None, refresh: bool = False, full_load: bool = False) -> 'TItemList':
        if self.platform is not None:
            if self._parent is None or refresh:
                self._parent = platform.get_parent(self)  # TODO implement full_load, full_load=full_load)
        else:
            raise self.NoPlatformException('Items require a platform object to resolve their parent_id to an object.')
        return self._parent

    def children(self, refresh: bool = False, full_load: bool = False) -> 'TItemList':
        if self.platform is not None:
            if self._children is None or refresh:
                self._children = self.platform.get_children(self)  # TODO implement full_load, full_load=full_load)
        else:
            raise self.NoPlatformException('Items require a platform object to resolve their children ids to objects.')
        return EntityContainer(self._children)
