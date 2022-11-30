"""
IEntity definition. IEntity is the base of most of our Remote server entitiies like Experiment, Simulation, WorkItems, and Suites.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from abc import ABCMeta
from dataclasses import dataclass, field
from os import PathLike
from typing import NoReturn, List, Any, Dict, Union, TYPE_CHECKING
from idmtools.core import EntityStatus, ItemType, NoPlatformException
from idmtools.core.interfaces.iitem import IItem
from idmtools.core.id_file import read_id_file, write_id_file
from idmtools.services.platforms import PlatformPersistService

if TYPE_CHECKING:  # pragma: no cover
    from idmtools.entities.iplatform import IPlatform


@dataclass
class IEntity(IItem, metaclass=ABCMeta):
    """
    Interface for all entities in the system.
    """
    #: ID of the platform
    platform_id: str = field(default=None, compare=False, metadata={"md": True})
    #: Platform
    _platform: 'IPlatform' = field(default=None, compare=False, metadata={"pickle_ignore": False})  # noqa E821
    #: Parent id
    parent_id: str = field(default=None, metadata={"md": True})
    #: Parent object
    _parent: 'IEntity' = field(default=None, compare=False, metadata={"pickle_ignore": False})
    #: Status of item
    status: EntityStatus = field(default=None, compare=False, metadata={"pickle_ignore": True})
    #: Tags for item
    tags: Dict[str, Any] = field(default_factory=lambda: {}, metadata={"md": True})
    #: Item Type(Experiment, Suite, Asset, etc)
    item_type: ItemType = field(default=None, compare=False)
    #: Platform Representation of Entity
    _platform_object: Any = field(default=None, compare=False, metadata={"pickle_ignore": True})

    def update_tags(self, tags: dict = None) -> NoReturn:
        """
        Shortcut to update the tags with the given dictionary.

        Args:
            tags: New tags
        """
        self.tags.update(tags)

    def post_creation(self, platform: 'IPlatform') -> None:
        """
        Post creation hook for object.

        Returns:
            None
        """
        self.status = EntityStatus.CREATED
        super().post_creation(platform)

    @classmethod
    def from_id_file(cls, filename: Union[PathLike, str], platform: 'IPlatform' = None, **kwargs) -> 'IEntity':  # noqa E821:
        """
        Load from a file that container the id.

        Args:
            filename: Filename to load
            platform: Platform object to load id from. This can be loaded from file if saved there.
            **kwargs: Platform extra arguments

        Returns:
            Entity loaded from id file

        Raises:
            EnvironmentError if item type is None.
        """
        item_id, item_type_in_file, platform_block, extra_args = read_id_file(filename)

        if platform is None:
            if platform_block:
                from idmtools.core.platform_factory import Platform
                platform = Platform(platform_block, **kwargs)
            else:
                platform = cls.get_current_platform_or_error()
        if cls.item_type is None:
            raise EnvironmentError("ItemType is None. This is most likely a badly derived IEntity that doesn't run set the default item type on the class")

        return platform.get_item(item_id, cls.item_type, **kwargs)

    @classmethod
    def from_id(cls, item_id: str, platform: 'IPlatform' = None, **kwargs) -> 'IEntity':  # noqa E821
        """
        Load an item from an id.

        Args:
            item_id: Id of item
            platform: Platform. If not supplied, we check the current context
            **kwargs: Optional platform args

        Returns:
            IEntity of object
        """
        if platform is None:
            platform = cls.get_current_platform_or_error()
        if cls.item_type is None:
            raise EnvironmentError("ItemType is None. This is most likely a badly derived IEntity that doesn't run set the default item type on the class")
        return platform.get_item(item_id, cls.item_type, **kwargs)

    @property
    def parent(self):
        """
        Return parent object for item.

        Returns:
            Parent entity if set
        """
        if not self._parent:
            if not self.parent_id:
                return None
            if not self.platform:
                raise NoPlatformException("The object has no platform set...")
            self._parent = self.platform.get_parent(self.uid, self.item_type)

        return self._parent

    @parent.setter
    def parent(self, parent: 'IEntity'): # noqa E821
        """
        Sets the parent object for item.

        Args:
            parent: Parent object

        Returns:
            None
        """
        if parent:
            self._parent = parent
            self.parent_id = parent.uid
        else:
            self.parent_id = self._parent = None

    @property
    def platform(self) -> 'IPlatform':  # noqa E821
        """
        Get objects platform object.

        Returns:
            Platform
        """
        if not self._platform and self.platform_id:
            self._platform = PlatformPersistService.retrieve(self.platform_id)
        return self._platform

    @platform.setter
    def platform(self, platform: 'IPlatform'):  # noqa E821
        """
        Sets object platform.

        Args:
            platform: Platform to set

        Returns:
            None
        """
        if platform:
            self.platform_id = platform.uid
            self._platform = platform
        else:
            self._platform = self.platform_id = None

    def get_platform_object(self, force: bool = False, platform: 'IPlatform' = None, **kwargs):
        """
        Get the platform representation of an object.

        Args:
            force: Force reload of platform object
            platform: Allow passing platform object to fetch
            **kwargs: Optional args used for specific platform behaviour

        Returns:
            Platform Object
        """
        if platform:
            self.platform = platform
        if not self.platform:
            raise NoPlatformException("The object has no platform set...")
        if self._platform_object is None or force:
            self._platform_object = self.platform.get_item(self.uid, self.item_type, raw=True, force=force, **kwargs)
        return self._platform_object

    @property
    def done(self):
        """
        Returns if a item is done.

        For an item to be done, it should be in either failed or succeeded state.

        Returns:
            True if status is succeeded or failed
        """
        return self.status in (EntityStatus.SUCCEEDED, EntityStatus.FAILED)

    @property
    def succeeded(self):
        """
        Returns if an item has succeeded.

        Returns:
            True if status is SUCCEEDED
        """
        return self.status == EntityStatus.SUCCEEDED

    @property
    def failed(self):
        """
        Returns is a item has failed.

        Returns:
            True if status is failed
        """
        return self.status == EntityStatus.FAILED

    def __hash__(self):
        """
        Returns hash for object. For entities, the hash is the id.

        Returns:
            Hash id
        """
        return id(self.uid)

    def _check_for_platform_from_context(self, platform) -> 'IPlatform':
        """
        Try to determine platform of current object from self or current platform.

        Args:
            platform: Passed in platform object

        Raises:
            NoPlatformException: when no platform is on current context
        Returns:
            Platform object
        """
        if self.platform is None:
            # check context for current platform
            if platform is None:
                platform = self.get_current_platform_or_error()
            self.platform = platform
        return self.platform

    @staticmethod
    def get_current_platform_or_error():
        """
        Try to fetch the current platform from context. If no platform is set, error.

        Returns:
            Platform if set

        Raises:
            NoPlatformException if no platform is set on the current context
        """
        from idmtools.core.context import get_current_platform
        p = get_current_platform()
        if p is None:
            raise NoPlatformException("No Platform defined on object, in current context, or passed to run")
        return p

    def to_id_file(self, filename: Union[str, PathLike], save_platform: bool = False, platform_args: Dict = None):
        """
        Write a id file.

        Args:
            filename: Filename to create
            save_platform: Save platform to the file as well
            platform_args: Platform Args

        Returns:
            None
        """
        write_id_file(filename, self, save_platform, platform_args)


IEntityList = List[IEntity]
