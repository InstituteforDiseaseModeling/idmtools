import ast
import typing
from abc import ABCMeta, abstractmethod
from dataclasses import field, fields
from itertools import groupby
from logging import getLogger

from idmtools.core.interfaces.ientity import IEntity, TEntityList, TEntity
from idmtools.core.interfaces.iitem import IItem
from idmtools.core import CacheEnabled, ItemType, UnknownItemException

if typing.TYPE_CHECKING:
    from idmtools.core.interfaces.iitem import TItem, TItemList
    from typing import Dict, List, NoReturn, Set
    from uuid import UUID

logger = getLogger(__name__)

CALLER_LIST = ['_create_from_block',  # create platform through Platform Factory
               'fetch',  # create platform through un-pickle
               'get',  # create platform through platform spec' get method
               '_main',
               '__newobj__']


class IPlatform(IItem, CacheEnabled, metaclass=ABCMeta):
    """
    Interface defining a platform.
    Interface defining a platform.
    A platform needs to implement basic operation such as:
    - Creating experiment
    - Creating simulation
    - Commissioning
    - File handling
    """
    supported_types: 'Set[ItemType]' = field(default_factory=lambda: set(), metadata={"pickle_ignore": True})
    _object_cache_expiration: 'int' = 60

    @staticmethod
    def get_caller():
        """
        Trace the stack and find the caller
        Returns: the direct caller
        """
        import inspect

        s = inspect.stack()
        return s[2][3]

    def __new__(cls, *args, **kwargs):
        """
        Here is the code to create a new object!
        Args:
            args: user inputs
            kwargs: user inputs
        Returns: object created
        """

        # Check the caller
        caller = cls.get_caller()

        # Action based on the caller
        if caller in CALLER_LIST:
            return super().__new__(cls)
        else:
            raise ValueError(
                f"Please use Factory to create Platform! For example: \n    platform = Platform('COMPS', **kwargs)")

    def __post_init__(self) -> 'NoReturn':
        """
        Work to be done after object creation
        Returns: None
        """
        self.validate_inputs_types()

    @abstractmethod
    def _create_batch(self, batch:'TEntityList', item_type:'ItemType') -> 'List[UUID]':
        pass

    def create_items(self, items: 'TEntity') -> 'List[UUID]':
        """
        Function creating e.g. sims/exps/suites on the platform.
        The function will batch the items based on type and call the self._create_batch for creation
        Args:
            items: All the items to create
        Returns: List of ids created
        """
        ids = []
        for key, group in groupby(items, lambda x: x.item_type):
            ids.extend(self._create_batch(list(group), key))
        return ids

    @abstractmethod
    def run_items(self, items: 'TItemList') -> 'NoReturn':
        """
        Run the items (sims, exps, suites) on the platform
        Args:
            items: The items to run
        """
        pass

    @abstractmethod
    def send_assets(self, item: 'TItem', **kwargs) -> 'NoReturn':
        """
        Send the assets for a given item (sim, experiment, suite, etc) to the platform.
        Args:
            item: The item to process. Expected to have an `assets` attribute containing the collection.
            **kwargs: Extra parameters used by the platform
        """
        pass

    @abstractmethod
    def refresh_status(self, item) -> 'NoReturn':
        """
        Populate the platform item and specified item with its status.
        Args:
            item: The item to check status for
        """
        pass

    def flatten_item(self, item: 'IEntity') -> 'TItemList':
        children = self.get_children(item.uid, item.item_type, force=True)
        if children is None:
            items = [item]
        else:
            items = list()
            for child in children:
                items += self.flatten_item(item=child)
        return items

    @abstractmethod
    def get_platform_item(self, item_id, item_type, **kwargs):
        pass

    @abstractmethod
    def _platform_item_to_entity(self, platform_item, **kwargs):
        pass

    @abstractmethod
    def get_children_for_platform_item(self, platform_item, raw, **kwargs):
        pass

    @abstractmethod
    def get_parent_for_platform_item(self, platform_item, raw, **kwargs):
        pass

    def get_item(self, item_id: 'UUID', item_type: 'ItemType' = None,
                 force: 'bool' = False, raw: 'bool' = False, **kwargs) -> any:
        """
        Retrieve an object from the platform.
        This function is cached, force allows to force the refresh of the cache.
        If no object_type passed: the function will try all the types (experiment, suite, simulation)
        Args:
            item_id: id of the object to retrieve
            item_type: Type of the object to be retrieved
            force: Force the object fetching from the platform
            raw: Return either an idmtools object or a platform object

        Returns: The object found on the platform or None
        """
        if not item_type or item_type not in self.supported_types:
            raise Exception("The provided type is invalid or not supported by this platform...")

        # Create the cache key
        cache_key = f"o_{item_id}_" + ('r' if raw else 'o') + '_'.join(f"{k}_{v}" for k, v in kwargs.items())

        # If force -> delete in the cache
        if force:
            self.cache.delete(cache_key)

        # If we cannot find the object in the cache -> retrieve depending on the type
        if cache_key not in self.cache:
            ce = self.get_platform_item(item_id, item_type, **kwargs)

            # Nothing was found on the platform
            if not ce:
                raise UnknownItemException(f"Object {item_type} {item_id} not found on the platform...")

            # Create the object if we do not want it raw
            if raw:
                return_object = ce
            else:
                return_object = self._platform_item_to_entity(ce, **kwargs)
                return_object.platform = self

            # Persist
            self.cache.set(cache_key, return_object, expire=self._object_cache_expiration)

        else:
            return_object = self.cache.get(cache_key)

        return return_object

    def get_children(self, item_id: 'uuid', item_type: 'ItemType',
                     force: 'bool' = False, raw: 'bool' = False, **kwargs) -> 'any':
        """
        Get the children of a given object.

        Args:
            item_id: id of the object for which we want the children
            force: Force the object fetching from the platform
            raw: Return either an idmtools object or a platform object
            item_type: Pass the type of the object for quicker retrieval

        Returns: Children of the object or None

        """
        if not item_type or item_type not in self.supported_types:
            raise Exception("The provided type is invalid or not supported by this platform...")

        cache_key = f"c_{item_id}" + ('r' if raw else 'o') + '_'.join(f"{k}_{v}" for k, v in kwargs.items())
        if force:
            self.cache.delete(cache_key)

        if cache_key not in self.cache:
            ce = self.get_item(item_id, raw=True, item_type=item_type)
            children = self.get_children_for_platform_item(ce, raw=raw, **kwargs)
            self.cache.set(cache_key, children, expire=self._object_cache_expiration)
            return children

        return self.cache.get(cache_key)

    def get_parent(self, object_id: 'uuid', object_type: 'ItemType' = None, force: 'bool' = False,
                   raw: 'bool' = False, **kwargs):
        """
        Get the parent of a given object.

        Args:
            object_id: id of the object for which we want the parent
            force: Force the object fetching from the platform
            raw: Return either an idmtools object or a platform object
            object_type: Pass the type of the object for quicker retrieval

        Returns: Parent of the object or None

        """
        if not object_type or object_type not in self.supported_types:
            raise Exception("The provided type is invalid or not supported by this platform...")

        cache_key = f'p_{object_id}' + ('r' if raw else 'o') + '_'.join(f"{k}_{v}" for k, v in kwargs.items())

        if force:
            self.cache.delete(cache_key)

        if cache_key not in self.cache:
            ce = self.get_item(object_id, raw=True, item_type=object_type)
            parent = self.get_parent_for_platform_item(ce, raw=raw, **kwargs)
            self.cache.set(cache_key, parent, expire=self._object_cache_expiration)
            return parent

        return self.cache.get(cache_key)

    @abstractmethod
    def get_files(self, item: 'TItem', files: 'List[str]') -> 'Dict[str, bytearray]':
        """
        Obtain specified files related to the given item (an Item, a base item)
        Args:
            item: item to retrieve file data for
            files: relative-path files to obtain

        Returns: a dict of file-path-keyed file data

        """
        pass

    def __repr__(self):
        return f"<Platform {self.__class__.__name__} - id: {self.uid}>"

    def validate_inputs_types(self) -> 'NoReturn':
        """
        Validate user inputs and case attr with the correct data types
        Returns: None
        """
        # retrieve field values, default values and types
        fds = fields(self)
        field_value = {f.name: getattr(self, f.name) for f in fds}
        field_type = {f.name: f.type for f in fds}

        # Make sure the user values have the requested type
        fs_kwargs = set(field_type.keys()).intersection(set(field_value.keys()))
        for fn in fs_kwargs:
            ft = field_type[fn]
            if ft in (int, float, str):
                field_value[fn] = ft(field_value[fn]) if field_value[fn] is not None else field_value[fn]
            elif ft is bool:
                field_value[fn] = ast.literal_eval(field_value[fn]) if isinstance(field_value[fn], str) else \
                    field_value[fn]

        # Update attr with validated data types
        for fn in fs_kwargs:
            setattr(self, fn, field_value[fn])


TPlatform = typing.TypeVar("TPlatform", bound=IPlatform)
TPlatformClass = typing.Type[TPlatform]
