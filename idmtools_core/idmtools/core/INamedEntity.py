import typing
from abc import ABCMeta

from idmtools.core import IEntity

if typing.TYPE_CHECKING:
    import uuid
    from idmtools.core import TTags


class INamedEntity(IEntity, metaclass=ABCMeta):
    def __init__(self, name:'str'=None, uid: 'uuid' = None, tags: 'TTags' = None):
        super().__init__(uid=uid, tags=tags)
        self.name = name

