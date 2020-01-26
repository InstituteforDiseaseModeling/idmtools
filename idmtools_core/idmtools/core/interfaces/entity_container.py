import typing

if typing.TYPE_CHECKING:
    from idmtools.core.interfaces.ientity import IEntity
    from typing import List


class EntityContainer(list):
    def __init__(self, children: 'List[IEntity]' = None):
        super().__init__()
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

