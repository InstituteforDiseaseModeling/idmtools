import typing

if typing.TYPE_CHECKING:
    from idmtools.core.interfaces.ientity import IEntity
    from typing import List



class ParentIterator:
    def __init__(self, lst: typing.Iterator, parent: 'IEntity'):
        self.items = lst
        self.parent = parent

    def __iter__(self):
        return self

    def __next__(self):
        i = next(self.items)
        i._parent = self.parent
        if hasattr(i, 'parent_id') and self.parent.uid is not None:
            i.parent_id = self.parent.uid
        return i



class EntityContainer(list):
    def __init__(self, children: 'List[IEntity]' = None, parent: 'IEntity' = None):
        super().__init__()
        self.parent = parent
        self.extend(children or [])

    def set_status(self, status):
        for entity in self:
            entity.status = status

    def set_status_for_item(self, item_id, status):
        for entity in self:
            if entity.uid == item_id:
                entity.status = status
                return

        raise Exception(f"Item with id {item_id} not found in the container")

    def __iter__(self):
        if self.parent is not None:
            return ParentIterator(super().__iter__(), self.parent)
        else:
            return super().__iter__()
