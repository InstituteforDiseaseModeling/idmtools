import typing
from abc import ABCMeta
from dataclasses import dataclass, field, fields
from uuid import UUID

from idmtools.core import EntityStatus, ObjectType
from idmtools.entities.iitem import IItem

if typing.TYPE_CHECKING:
    from idmtools.core import TTags
    from idmtools.entities.iplatform import TPlatform


@dataclass(unsafe_hash=True)
class IEntity(IItem, metaclass=ABCMeta):
    """
    Interface for all entities in the system.
    """

    platform_id: 'UUID' = field(default=None, metadata={"md": True})
    _platform: 'TPlatform' = field(default=None, compare=False, metadata={"pickle_ignore": True})
    parent_id: 'UUID' = field(default=None, metadata={"md": True})
    _parent: 'IEntity' = field(default=None, compare=False, metadata={"pickle_ignore": True})
    status: 'EntityStatus' = field(default=None, compare=False, metadata={"pickle_ignore": True})
    tags: 'TTags' = field(default_factory=lambda: {}, metadata={"md": True})
    object_type: 'ObjectType' = field(default=None)

    @property
    def parent(self):
        if not self._parent:
            if not self.parent_id:
                return None
            self._parent = self.platform.get_parent(self.parent_id, ObjectType.SIMULATION)

        return self._parent

    @parent.setter
    def parent(self, parent):
        if parent:
            self._parent = parent
            self.parent_id = parent.uid
        else:
            self.parent_id = self._parent = None

    @property
    def platform(self):
        return self._platform

    @platform.setter
    def platform(self, platform):
        if platform:
            self.platform_id = platform.uid
            self._platform = platform
        else:
            self._platform = self.platform_id = None

    def get_platform_object(self, force=False, **kwargs):
        if not self.platform:
            raise Exception("The object has no platform set...")

        return self.platform.get_object(self.uid, self.object_type, raw=True, force=force, **kwargs)

    @property
    def done(self):
        return self.status in (EntityStatus.SUCCEEDED, EntityStatus.FAILED)

    @property
    def succeeded(self):
        return self.status == EntityStatus.SUCCEEDED

