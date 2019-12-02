from abc import ABCMeta, abstractmethod
from dataclasses import fields
from itertools import groupby
from logging import getLogger
from uuid import UUID
from idmtools.core import CacheEnabled, ItemType, UnknownItemException, EntityContainer, UnsupportedPlatformType
from idmtools.core.interfaces.ientity import IEntity
from idmtools.entities import IExperiment
from idmtools.entities.iexperiment import IDockerExperiment, IGPUExperiment
from idmtools.entities.iplatform_metadata import IPlatformExperimentOperations, \
    IPlatformSimulationOperations, IPlatformSuiteOperations, IPlatformWorkflowItemOperations, \
    IPlatformAssetCollectionOperations
from idmtools.services.platforms import PlatformPersistService
from idmtools.core.interfaces.iitem import IItem, IItemList
from typing import Dict, List, NoReturn, Type, TypeVar, Any, Union

from idmtools.utils.entities import validate_user_inputs_against_dataclass

logger = getLogger(__name__)

CALLER_LIST = ['_create_from_block',    # create platform through Platform Factory
               'fetch',                 # create platform through un-pickle
               'get',                   # create platform through platform spec' get method
               '__newobj__',            # create platform through copy.deepcopy
               '_main']                 # create platform through analyzer manager


item_type_to_object_interface = {
    ItemType.EXPERIMENT: '_experiments',
    ItemType.SIMULATION: '_simulations',
    ItemType.SUITE: '_suites',
    ItemType.WORKFLOW_ITEM: '_workflow_items',
    ItemType.ASSETCOLLECTION: '_assets'
}


class IPlatform(IItem, CacheEnabled, metaclass=ABCMeta):
    """
    Interface defining a platform.
    A platform needs to implement basic operation such as:

    - Creating experiment
    - Creating simulation
    - Commissioning
    - File handling
    """
    platform_type_map: Dict[Type, ItemType] = None
    _object_cache_expiration: 'int' = 60

    _experiments: IPlatformExperimentOperations = None
    _simulations: IPlatformSimulationOperations = None
    _suites: IPlatformSuiteOperations = None
    _workflow_items: IPlatformWorkflowItemOperations = None
    _assets: IPlatformAssetCollectionOperations = None

    @staticmethod
    def get_caller():
        """
        Trace the stack and find the caller.

        Returns:
            The direct caller.
        """
        import inspect

        s = inspect.stack()
        return s[2][3]

    def __new__(cls, *args, **kwargs):
        """
        Create a new object.

        Args:
            args: User inputs.
            kwargs: User inputs.

        Returns:
            The object created.
        """

        # Check the caller
        caller = cls.get_caller()

        # Action based on the caller
        if caller in CALLER_LIST:
            return super().__new__(cls)
        else:
            raise ValueError(
                f"Please use Factory to create Platform! For example: \n    platform = Platform('COMPS', **kwargs)")

    def __post_init__(self) -> NoReturn:
        """
        Work to be done after object creation.

        Returns:
            None
        """
        # build item type map and determined supported features
        self.platform_type_map = dict()
        for item_type, interface in item_type_to_object_interface.items():
            if getattr(self, interface) is not None and getattr(self, interface).platform_type is not None:
                self.platform_type_map[getattr(self, interface).platform_type] = item_type

        self.validate_inputs_types()

        # Initialize the cache
        self.initialize_cache()

        # Save itself
        PlatformPersistService.save(self)

    def validate_inputs_types(self) -> NoReturn:
        """
        Validate user inputs and case attributes with the correct data types.

        Returns:
            None
        """
        # retrieve field values, default values and types
        fds = fields(self)
        field_value = {f.name: getattr(self, f.name) for f in fds}
        field_type = {f.name: f.type for f in fds}

        # Make sure the user values have the requested type
        fs_kwargs = validate_user_inputs_against_dataclass(field_type, field_value)

        # Update attr with validated data types
        for fn in fs_kwargs:
            setattr(self, fn, field_value[fn])

    def _get_platform_item(self, item_id: UUID, item_type: ItemType, **kwargs) -> Any:
        """
        Get an item by its ID. The implementing classes must know how to distinguish
        items of different levels (e.g. simulation, experiment, suite).

        Args:
            item_id: The ID of the item to retrieve.
            item_type: The type of object to retrieve.

        Returns:
            The specified item found on the platform or None.
        """
        if item_type not in self.platform_type_map.values():
            raise ValueError(f"Unsupported Item Type. {self.__class__.__name__} only supports "
                             f"{self.platform_type_map.values()}")
        interface = item_type_to_object_interface[item_type]
        return getattr(self, interface).get(item_id, **kwargs)

    def get_item(self, item_id: UUID, item_type: ItemType = None,
                 force: bool = False, raw: bool = False, **kwargs) -> Any:
        """
        Retrieve an object from the platform.
        This function is cached; force allows you to force the refresh of the cache.
        If no **object_type** is passed, the function will try all the types (experiment, suite, simulation).

        Args:
            item_id: The ID of the object to retrieve.
            item_type: The type of the object to be retrieved.
            force: If True, force the object fetching from the platform.
            raw: Return either an |IT_s| object or a platform object.

        Returns:
            The object found on the platform or None.
        """
        if not item_type or item_type not in self.platform_type_map.values():
            raise Exception("The provided type is invalid or not supported by this platform...")

        # Create the cache key
        cache_key = f"o_{item_id}_" + ('r' if raw else 'o') + '_'.join(f"{k}_{v}" for k, v in kwargs.items())

        # If force -> delete in the cache
        if force:
            self.cache.delete(cache_key)

        # If we cannot find the object in the cache -> retrieve depending on the type
        if cache_key not in self.cache:
            ce = self._get_platform_item(item_id, item_type, **kwargs)

            # Nothing was found on the platform
            if not ce:
                raise UnknownItemException(f"Object {item_type} {item_id} not found on the platform...")

            # Create the object if we do not want it raw
            if raw:
                return_object = ce
            else:
                return_object = self._convert_platform_item_to_entity(ce, **kwargs)
                return_object._platform_object = ce
                return_object.platform = self

            # Persist
            self.cache.set(cache_key, return_object, expire=self._object_cache_expiration)

        else:
            return_object = self.cache.get(cache_key)

        return return_object

    def _get_platform_children_for_item(self, item: Any, raw: bool = False, **kwargs) -> List[Any]:
        ent_opts = {}
        if item.__class__ not in self.platform_type_map:
            raise ValueError(f"{self.__class__.__name__} has no mapping for {item.__class__.__name__}")
        it = self.platform_type_map[item.__class__]
        if it == ItemType.EXPERIMENT:
            children = self._experiments.get_children(item, **kwargs)
        elif it == ItemType.SUITE:
            children = self._suites.get(item, **kwargs)
        else:
            raise ValueError("Only suites and experiments have children")
        if not raw:
            ret = []
            for e in children:
                n = self._convert_platform_item_to_entity(e, **ent_opts)
                n._platform_object = e
                ret.append(n)
            return EntityContainer(ret)
        else:
            return children

    def get_children(self, item_id: UUID, item_type: ItemType,
                     force: bool = False, raw: bool = False, **kwargs) -> Any:
        """
        Retrieve the children of a given object.

        Args:
            item_id: The ID of the object for which we want the children.
            force: If True, force the object fetching from the platform.
            raw: Return either an |IT_s| object or a platform object.
            item_type: Pass the type of the object for quicker retrieval.

        Returns:
            The children of the object or None.
        """
        if not item_type or item_type not in self.platform_type_map.values():
            raise Exception("The provided type is invalid or not supported by this platform...")

        # Create the cache key based on everything we pass to the function
        cache_key = f"c_{item_id}" + ('r' if raw else 'o') + '_'.join(f"{k}_{v}" for k, v in kwargs.items())

        if force:
            self.cache.delete(cache_key)

        if cache_key not in self.cache:
            ce = self.get_item(item_id, raw=True, item_type=item_type)
            children = self._get_platform_children_for_item(ce, raw=raw, **kwargs)
            self.cache.set(cache_key, children, expire=self._object_cache_expiration)
            return children

        return self.cache.get(cache_key)

    def _get_parent_for_platform_item(self, platform_item: Any, raw: bool, **kwargs) -> Any:
        """
        Return the parent item for a given platform_item.

        Args:
            platform_item: Child item
            raw: Return a platform item if True, an idm-tools entity if false
            **kwargs: Additional platform specific parameters

        Returns:
            Parent or None
        """
        if type(platform_item) not in self.platform_type_map.values():
            raise UnsupportedPlatformType("The provided type is invalid or not supported by this platform...")
        item_type = self.platform_type_map[type(platform_item)]
        if item_type not in [ItemType.EXPERIMENT, ItemType.SUITE]:
            raise ValueError("Currently only Experiments and Suites supported children")

        interface = item_type_to_object_interface[item_type]
        return getattr(self, interface).get_children(platform_item, raw, **kwargs)

    def get_parent(self, item_id: UUID, item_type: ItemType = None, force: bool = False,
                   raw: bool = False, **kwargs):
        """
        Retrieve the parent of a given object.

        Args:
            item_id: The ID of the object for which we want the parent.
            force: If True, force the object fetching from the platform.
            raw: Return either an |IT_s| object or a platform object.
            item_type: Pass the type of the object for quicker retrieval.

        Returns:
            The parent of the object or None.

        """
        if not item_type or item_type not in self.platform_type_map.values():
            raise UnsupportedPlatformType("The provided type is invalid or not supported by this platform...")

        # Create the cache key based on everything we pass to the function
        cache_key = f'p_{item_id}' + ('r' if raw else 'o') + '_'.join(f"{k}_{v}" for k, v in kwargs.items())

        if force:
            self.cache.delete(cache_key)

        if cache_key not in self.cache:
            ce = self.get_item(item_id, raw=True, item_type=item_type)
            parent = self._get_parent_for_platform_item(ce, raw=raw, **kwargs)
            self.cache.set(cache_key, parent, expire=self._object_cache_expiration)
            return parent

        return self.cache.get(cache_key)

    def create_items(self, items: List[IEntity]) -> List[UUID]:
        """
        Create items (simulations, experiments, or suites) on the platform. The function will batch the items based on
        type and call the self._create_batch for creation
        Args:
            items: The list of items to create.
        Returns:
            List of item IDs created.
        """
        self._is_item_list_supported(items)

        ids = []
        for key, group in groupby(items, lambda x: x.item_type):
            interface = item_type_to_object_interface[key]
            group_ids = getattr(self, interface).batch_create(list(group))
            ids.extend([i[1] for i in group_ids])
        return ids

    def _is_item_list_supported(self, items: List[IEntity]):
        for item in items:
            if item.item_type not in self.platform_type_map.values():
                raise Exception(
                    f'Unable to create items of type: {item.item_type} for platform: {self.__class__.__name__}')

    def run_items(self, items: List[IEntity]):
        self._is_item_list_supported(items)

        for item in items:
            interface = item_type_to_object_interface[item.item_type]
            getattr(self, interface).run_item(item)

    @abstractmethod
    def supported_experiment_types(self) -> List[Type]:
        """
        Returns a list of supported experiment types. These types should be either abstract or full classes that have
            been derived from IExperiment
        Returns:

        """
        return [IExperiment]

    @abstractmethod
    def unsupported_experiment_types(self) -> List[Type]:
        """
        Returns a list of experiment types not supported by the platform. These types should be either abstract or full
            classes that have been derived from IExperiment
        Returns:

        """
        return [IDockerExperiment, IGPUExperiment]

    def is_supported_experiment(self, experiment: IExperiment) -> bool:
        """
        Determines if an experiment is supported by the specified platform.
        Args:
            experiment: Experiment to check

        Returns:
            True is experiment is supported, otherwise, false
        """
        ex_types = set(self.supported_experiment_types())
        if any([isinstance(experiment, t) for t in ex_types]):
            unsupported_types = self.unsupported_experiment_types()
            return not any([isinstance(experiment, t) for t in unsupported_types])
        return False

    def __repr__(self):
        return f"<Platform {self.__class__.__name__} - id: {self.uid}>"

    def _convert_platform_item_to_entity(self, platform_item: Any, **kwargs) -> IEntity:
        for src_type, dest_type in self.platform_type_map.items():
            if isinstance(platform_item, src_type):
                interface = item_type_to_object_interface[dest_type]
                return getattr(self, interface).to_entity(platform_item)
        return platform_item

    def flatten_item(self, item: IEntity) -> IItemList:
        """
        Flatten an item: resolve the children until getting to the leaves.
        For example, for an experiment, will return all the simulations.
        For a suite, will return all the simulations contained in the suites experiments.

        Args:
            item: Which item to flatten

        Returns:List of leaves

        """
        children = self.get_children(item.uid, item.item_type, force=True)
        if children is None:
            items = [item]
        else:
            items = list()
            for child in children:
                items += self.flatten_item(item=child)
        return items

    def refresh_status(self, item: IEntity) -> NoReturn:
        """
        Populate the platform item and specified item with its status.

        Args:
            item: The item to check status for.
        """
        if item.item_type not in self.platform_type_map.values():
            raise UnsupportedPlatformType("The provided type is invalid or not supported by this platform...")
        interface = item_type_to_object_interface[item.item_type]
        getattr(self, interface).refresh_status(item)

    def get_files(self, item: IEntity, files: List[str]) -> Union[Dict[str, Dict[str, bytearray]], Dict[str, bytearray]]:
        if item.item_type not in self.platform_type_map.values():
            raise UnsupportedPlatformType("The provided type is invalid or not supported by this platform...")
        interface = item_type_to_object_interface[item.item_type]
        return getattr(self, interface).get_assets(item, files)


TPlatform = TypeVar("TPlatform", bound=IPlatform)
TPlatformClass = Type[TPlatform]
