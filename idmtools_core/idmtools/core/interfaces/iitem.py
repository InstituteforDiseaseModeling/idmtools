from dataclasses import dataclass, field, fields
from typing import List, Callable, TYPE_CHECKING
from uuid import UUID
from idmtools.utils.hashing import hash_obj, ignore_fields_in_dataclass_on_pickle
if typing.TYPE_CHECKING:
    from idmtools.entities.iplatform import IPlatform

if TYPE_CHECKING:
    from idmtools.entities import IPlatform


@dataclass(repr=False)
class IItem:
    _uid: UUID = field(default=None, metadata={"md": True})
    __pre_creation_hooks: List[Callable[['IItem', 'IPlatform'], None]] = field(default_factory=list, metadata={"md": True})
    __post_creation_hooks: List[Callable[['IItem', 'IPlatform'], None]] = field(default_factory=list, metadata={"md": True})

    @property
    def uid(self):
        return hash_obj(self) if self._uid is None else self._uid

    @uid.setter
    def uid(self, uid):
        self._uid = uid

    @property
    def id(self):
        if self.uid:
            return str(self.uid)
        else:
            return self.uid

    @property
    def metadata(self):
        attrs = set(vars(self).keys())
        obj_dict = {k: getattr(self, k) for k in attrs.intersection(self.metadata_fields)}
        return self.__class__(**obj_dict)

    @property
    def pickle_ignore_fields(self):
        return set(f.name for f in fields(self) if "pickle_ignore" in f.metadata and f.metadata["pickle_ignore"])

    @property
    def metadata_fields(self):
        return set(f.name for f in fields(self) if "md" in f.metadata and f.metadata["md"])

    def display(self):
        return self.__repr__()

    # region Events methods
    def pre_creation(self, platform: 'IPlatform') -> None:
        """
        Called before the actual creation of the entity.

        Args:
            platform: Platform item is being created on

        Returns:

        """
        pass

    def post_creation(self, platform: 'IPlatform') -> None:
        """
        Called after the actual creation of the entity.

        Args:
            platform: Platform item was created on

        Returns:

        """
        pass

    def post_setstate(self):
        """
        Function called after restoring the state if additional initialization is required
        """
        pass

    def pre_getstate(self):
        """
        Function called before picking and return default values for "pickle-ignore" fields
        """
        pass

    # endregion

    # region State management
    def __getstate__(self):
        """
        Ignore the fields in pickle_ignore_fields during pickling.
        """
        return ignore_fields_in_dataclass_on_pickle(self)

    def __setstate__(self, state):
        """
        Add ignored fields back since they don't exist in the pickle
        """
        self.__dict__.update(state)

        # Restore the pickle fields with values requested
        self.post_setstate()
    # endregion


IItemList = List[IItem]
