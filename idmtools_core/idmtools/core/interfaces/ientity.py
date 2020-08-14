from abc import ABCMeta
from dataclasses import dataclass, field
from typing import NoReturn, List, Any, Dict, Union, TYPE_CHECKING
from uuid import UUID

from idmtools.core import EntityStatus, ItemType, NoPlatformException
from idmtools.core.interfaces.iitem import IItem
from idmtools.services.platforms import PlatformPersistService

if TYPE_CHECKING:
    from idmtools.entities.iplatform import IPlatform


@dataclass
class IEntity(IItem, metaclass=ABCMeta):
    """
    Interface for all entities in the system.
    """
    #: ID of the platform
    platform_id: UUID = field(default=None, compare=False, metadata={"md": True})
    #: Platform
    _platform: 'IPlatform' = field(default=None, compare=False, metadata={"pickle_ignore": True})  # noqa E821
    #: Parent id
    parent_id: UUID = field(default=None, metadata={"md": True})
    #: Parent object
    _parent: 'IEntity' = field(default=None, compare=False, metadata={"pickle_ignore": True})
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
        Shortcut to update the tags with the given dictionary
        Args:
            tags: New tags
        """
        self.tags.update(tags)

    def post_creation(self) -> None:
        """
        Post creation hook for object
        Returns:

        """
        self.status = EntityStatus.CREATED

    @classmethod
    def from_id(cls, item_id: Union[str, UUID], platform: 'IPlatform' = None, **kwargs) -> 'IEntity':  # noqa E821
        """
        Load an item from an id

        Args:
            item_id: Id of item
            platform: Platform. If not supplied, we check the current context
            **kwargs: Optional platform args

        Returns:
            IEntity of object
        """
        if platform is None:
            from idmtools.core.context import CURRENT_PLATFORM
            if CURRENT_PLATFORM is None:
                raise ValueError("You have to specify a platform to load the item from")
            platform = CURRENT_PLATFORM
        if cls.item_type is None:
            raise EnvironmentError("ItemType is None. This is most likely a badly derived IEntity "
                                   "that doesn't run set the default item type on the class")
        return platform.get_item(item_id, cls.item_type, **kwargs)

    @property
    def parent(self):
        """
        Return parent object for item
        Returns:

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
        Sets the parent object for item
        Args:
            parent: Parent oject

        Returns:

        """
        if parent:
            self._parent = parent
            self.parent_id = parent.uid
        else:
            self.parent_id = self._parent = None

    @property
    def platform(self) -> 'IPlatform':  # noqa E821
        """
        Get objects platform

        Returns:
            Platform
        """
        if not self._platform and self.platform_id:
            self._platform = PlatformPersistService.retrieve(self.platform_id)
        return self._platform

    @platform.setter
    def platform(self, platform: 'IPlatform'):  # noqa E821
        """
        Sets object platform

        Args:
            platform: Platform to set

        Returns:

        """
        if platform:
            self.platform_id = platform.uid
            self._platform = platform
        else:
            self._platform = self.platform_id = None

    def get_platform_object(self, force: bool=False, **kwargs):
        """
        Get the platform representation of an object

        Args:
            force: Force reload of platform object
            **kwargs: Optional args used for specific platform behaviour

        Returns:
            Platform Object
        """
        if not self.platform:
            raise NoPlatformException("The object has no platform set...")

        if self._platform_object is None or force:
            self._platform_object = self.platform.get_item(self.uid, self.item_type, raw=True, force=force, **kwargs)
        return self._platform_object

    @property
    def done(self):
        """
        Returns if a item is done. For an item to be done, it should be in either failed or succeeded state

        Returns:
            True if status is succeeded or failed
        """
        return self.status in (EntityStatus.SUCCEEDED, EntityStatus.FAILED)

    @property
    def succeeded(self):
        """
        Returns if an item has succeeded

        Returns:
            True if status is SUCCEEDED
        """
        return self.status == EntityStatus.SUCCEEDED

    @property
    def failed(self):
        """
        Returns is a item has failed

        Returns:
            True if status is failed
        """
        return self.status == EntityStatus.FAILED

    def __hash__(self):
        return id(self.uid)

    def _check_for_platform_from_context(self, platform) -> 'IPlatform':
        """
        Try to determine platform of current object from self or current platform

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
                from idmtools.core.context import CURRENT_PLATFORM
                if CURRENT_PLATFORM is None:
                    raise NoPlatformException("No Platform defined on object, in current context, or passed to run")
                platform = CURRENT_PLATFORM
            self.platform = platform
        return self.platform


IEntityList = List[IEntity]
