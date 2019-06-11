import typing

if typing.TYPE_CHECKING:
    from idmtools.core import IEntity


class EntityContainer(list):

    def __init__(self, children: 'List[IEntity]' = None):
        super().__init__()
        self.extend(children or [])

