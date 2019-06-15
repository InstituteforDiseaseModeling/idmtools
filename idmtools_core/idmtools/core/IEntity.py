import typing
from abc import ABCMeta

from idmtools.core import IPicklableObject
from idmtools.utils.hashing import hash_obj

if typing.TYPE_CHECKING:
    import uuid
    from idmtools.core import TTags


class IEntity(IPicklableObject, metaclass=ABCMeta):
    """
    Interface for all entities in the system.
    """

    def __init__(self, uid: 'uuid' = None, tags: 'TTags' = None):
        super().__init__()
        self._uid = uid
        self.tags = tags or {}
        self.platform_id = None

    @property
    def uid(self):
        return self._uid or hash_obj(self)

    @uid.setter
    def uid(self, uid):
        self._uid = uid

    def display(self):
        return self.__repr__()

    # region Events methods
    def pre_creation(self) -> None:
        """
        Called before the actual creation of the entity.
        """
        pass

    def post_creation(self) -> None:
        """
        Called after the actual creation of the entity.
        """
        pass

    # endregion

    # region State management
    def __eq__(self, other):
        return self.uid == other.uid
    # endregion
