import typing

if typing.TYPE_CHECKING:
    from idmtools.core import IEntity
    from typing import List


class EntityContainer(list):
    def __init__(self, children: 'List[IEntity]' = None):
        super().__init__()
        self.extend(children or [])

    def set_status(self, status):
        for entity in self:
            entity.status = status
