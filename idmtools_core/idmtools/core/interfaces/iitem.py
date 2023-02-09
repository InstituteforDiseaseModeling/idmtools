"""
IItem is the base of all items that have ids such as AssetCollections, Experiments, etc.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from dataclasses import dataclass, field, fields
from functools import lru_cache
from inspect import signature
from logging import getLogger, DEBUG
from typing import List, Callable, TYPE_CHECKING, Any, Dict

from idmtools import IdmConfigParser
from idmtools.registry.functions import FunctionPluginManager
from idmtools.utils.hashing import ignore_fields_in_dataclass_on_pickle

if TYPE_CHECKING:  # pragma: no cover
    from idmtools.entities.iplatform import IPlatform

logger = getLogger(__name__)

PRE_POST_CREATION_HOOK = Callable[['IItem', 'IPlatform'], None]


@lru_cache(maxsize=None)
def get_id_generator():
    """
    Retrieves the type of id generator specified in .ini config as well as corresponding plugin.

    Returns:
        id_gen: specified id generation plugin in .ini config (uuid, item_sequence, etc)
        plugin: id generation plugin that is used to determine ids for items. See setup.py > entry_points > idmtools_hooks for full names of plugin options
    """
    fpm = FunctionPluginManager.instance()
    id_gen = IdmConfigParser.get_option(None, "id_generator", "uuid")
    plugin = fpm.get_plugin(f"idmtools_id_generate_{id_gen}")
    return id_gen, plugin


@dataclass(repr=False)
class IItem:
    """
    IItem represents items that have identifiable ids.

    In addition, IItem facilities pre and post creation hooks through the __pre_creation_hooks, __post_creation_hooks, add_pre_creation_hook, add_post_creation_hook

    """
    _uid: str = field(default=None, metadata={"md": True})
    __pre_creation_hooks: List[PRE_POST_CREATION_HOOK] = field(default_factory=list, metadata={"md": True})
    __post_creation_hooks: List[PRE_POST_CREATION_HOOK] = field(default_factory=list, metadata={"md": True})

    @property
    def uid(self):
        """
        UID Of the object.

        If not id is set, uses the hash of the object.

        Returns:
            ID
        """
        if self._uid is None:
            id_gen, plugin = get_id_generator()
            if plugin:
                self._uid = plugin.idmtools_generate_id(self)
            else:
                fpm = FunctionPluginManager.instance()
                id_plugins = sorted([x[0] for x in fpm.list_name_plugin() if x[0].startswith("idmtools_id_generate_")])
                raise RuntimeError(f"Could not find the id plugin idmtools_id_generate_{id_gen} defined by id_generator in your idmtools.ini."
                                   f"Please use one of the following plugins: {', '.join(id_plugins)}")
        return self._uid

    @uid.setter
    def uid(self, uid):
        """
        Set the uid on the objects.

        Args:
            uid: Uid to set

        Returns:
            None
        """
        self._uid = uid

    @property
    def id(self):
        """
        Alias for uid.

        Returns:
            UID of object

        Notes:
            What is relation to uid?
        """
        if self.uid:
            return str(self.uid)
        else:
            return self.uid

    @property
    def metadata(self) -> Dict[str, Any]:
        """
        Identify the metadata from the fields.

        Returns:
            Metadata dict
        """
        attrs = set(vars(self).keys())
        obj_dict = {k: getattr(self, k) for k in attrs.intersection(self.metadata_fields)}
        return obj_dict

    @property
    def pickle_ignore_fields(self):
        """
        Get list of fields that will be ignored when pickling.

        Returns:
            Set of fields that are ignored when pickling the item
        """
        return set(f.name for f in fields(self) if "pickle_ignore" in f.metadata and f.metadata["pickle_ignore"])

    @property
    def metadata_fields(self):
        """
        Get list of fields that have metadata.

        Returns:
            Set of fields that have metadata
        """
        return set(f.name for f in fields(self) if "md" in f.metadata and f.metadata["md"])

    def display(self) -> str:
        """
        Display as string representation.

        Returns:
            String of item
        """
        return self.__repr__()

    # region Events methods
    def pre_creation(self, platform: 'IPlatform') -> None:
        """
        Called before the actual creation of the entity.

        Args:
            platform: Platform item is being created on

        Returns:
            None
        """
        for hook in self.__pre_creation_hooks:
            if logger.isEnabledFor(DEBUG):
                logger.debug(f'Calling pre-create hook named {hook.__name__ if hasattr(hook, "__name__") else str(hook)}')
            hook(self, platform)

    def post_creation(self, platform: 'IPlatform') -> None:
        """
        Called after the actual creation of the entity.

        Args:
            platform: Platform item was created on

        Returns:
            None
        """
        for hook in self.__post_creation_hooks:
            if logger.isEnabledFor(DEBUG):
                logger.debug(f'Calling post-create hook named {hook.__name__ if hasattr(hook, "__name__") else str(hook)}')
            hook(self, platform)

    def add_pre_creation_hook(self, hook: PRE_POST_CREATION_HOOK):
        """
        Adds a hook function to be called before an item is created.

        Args:
            hook: Hook function. This should have two arguments, the item and the platform

        Returns:
            None
        """
        if len(signature(hook).parameters) != 2:
            raise ValueError("Pre creation hooks should have 2 arguments. The first argument will be the item, the second the platform")
        self.__pre_creation_hooks.append(hook)

    def add_post_creation_hook(self, hook: PRE_POST_CREATION_HOOK):
        """
        Adds a hook function to be called after an item is created.

        Args:
            hook: Hook function. This should have two arguments, the item and the platform

        Returns:
            None
        """
        if len(signature(hook).parameters) != 2:
            raise ValueError("Post creation hooks should have 2 arguments. The first argument will be the item, the second the platform")
        self.__post_creation_hooks.append(hook)

    def post_setstate(self):
        """
        Function called after restoring the state if additional initialization is required.
        """
        pass

    def pre_getstate(self):
        """
        Function called before picking and return default values for "pickle-ignore" fields.
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
        Add ignored fields back since they don't exist in the pickle.
        """
        self.__dict__.update(state)

        # Restore the pickle fields with values requested
        self.post_setstate()
    # endregion


IItemList = List[IItem]
