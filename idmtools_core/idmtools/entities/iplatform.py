from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, fields, field
from itertools import groupby
from logging import getLogger
from uuid import UUID
from idmtools.core import CacheEnabled, ItemType, UnknownItemException, EntityContainer, UnsupportedPlatformType
from idmtools.core.interfaces.ientity import IEntity
from idmtools.entities.isimulation import ISimulation
from idmtools.entities.iworkflow_item import IWorkflowItem
from idmtools.entities.platform_requirements import PlatformRequirements
from idmtools.entities.suite import Suite
from idmtools.entities.iexperiment import IDockerExperiment, IGPUExperiment, IExperiment
from idmtools.entities.iplatform_metadata import IPlatformExperimentOperations, \
    IPlatformSimulationOperations, IPlatformSuiteOperations, IPlatformWorkflowItemOperations, \
    IPlatformAssetCollectionOperations, IPlatformWorkItemOperations
from idmtools.services.platforms import PlatformPersistService
from idmtools.core.interfaces.iitem import IItem, IItemList
from typing import Dict, List, NoReturn, Type, TypeVar, Any, Union, Tuple, Set

from idmtools.utils.entities import validate_user_inputs_against_dataclass

logger = getLogger(__name__)

CALLER_LIST = ['_create_from_block',    # create platform through Platform Factory
               'fetch',                 # create platform through un-pickle
               'get',                   # create platform through platform spec' get method
               '__newobj__',            # create platform through copy.deepcopy
               '_main']                 # create platform through analyzer manager

# Maps an object type to a platform interface object. We use strings to use getattr. This also let's us also reduce
# all the if else crud
ITEM_TYPE_TO_OBJECT_INTERFACE = {
    ItemType.EXPERIMENT: '_experiments',
    ItemType.SIMULATION: '_simulations',
    ItemType.SUITE: '_suites',
    ItemType.WORKFLOW_ITEM: '_workflow_items',
    ItemType.ASSETCOLLECTION: '_assets'
}
STANDARD_TYPE_TO_INTERFACE = {
    IExperiment: ItemType.EXPERIMENT,
    ISimulation: ItemType.SIMULATION,
    IWorkflowItem: ItemType.WORKFLOW_ITEM,
    Suite: ItemType.SUITE
}


@dataclass(repr=False)
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

    supported_types: Set[ItemType] = field(default_factory=lambda: set(), metadata={"pickle_ignore": True})
    _platform_supports: List[PlatformRequirements] = field(default_factory=list)

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

        try:
            s = inspect.stack()
        except RuntimeError:
            # in some high thread environments and under heavy load, we can get environment changes before retrieving
            # stack in those case assume we are good
            return "__newobj__"
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
        for item_type, interface in ITEM_TYPE_TO_OBJECT_INTERFACE.items():
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
        interface = ITEM_TYPE_TO_OBJECT_INTERFACE[item_type]
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

        cache_key = self.get_cache_key(force, item_id, item_type, kwargs, raw, 'r' if raw else 'o')

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
                if return_object._platform_object is None:
                    return_object._platform_object = ce
                return_object.platform = self

            # Persist
            self.cache.set(cache_key, return_object, expire=self._object_cache_expiration)

        else:
            return_object = self.cache.get(cache_key)

        return return_object

    def _get_children_for_platform_item(self, item: Any, raw: bool = True, **kwargs) -> List[Any]:
        """
        Returns the children for a platform object. For example, A Comps Experiment or Simulation

        The children can either be returns as native platform objects or as idmtools objects.

        Args:
            item: Item to fetch children for
            raw: When true, return the native platform representation of  the children, otherwise return the idmtools
                implementation
            **kwargs:

        Returns:
            Children of platform object
        """
        ent_opts = {}
        item_type, interface = self._get_operation_interface(item)
        if item_type in [ItemType.EXPERIMENT, ItemType.SUITE]:
            children = getattr(self, ITEM_TYPE_TO_OBJECT_INTERFACE[item_type]).get_children(item, **kwargs)
        else:
            return []
        if not raw:
            ret = []
            for e in children:
                n = self._convert_platform_item_to_entity(e, **ent_opts)
                if n._platform_object is None:
                    n._platform_object = e
                ret.append(n)
            return EntityContainer(ret)
        else:
            return children

    def _get_operation_interface(self, item: Any) -> Tuple[ItemType, str]:
        """
        Get the base item type and the interface string for said item. For example, on COMPSPlatform, if you passed a
        COMPSExperiment object, the function would return ItemType.Experiment, _experiments


        Args:
            item: Item to look up

        Returns:
            Tuple with the Base item type and the string path to the interface
        """
        # check both base types and platform speci
        for l in [STANDARD_TYPE_TO_INTERFACE, self.platform_type_map]:
            for interface, item_type in l.items():
                if isinstance(item, interface):
                    return item_type, ITEM_TYPE_TO_OBJECT_INTERFACE[item_type]
        raise ValueError(f"{self.__class__.__name__} has no mapping for {item.__class__.__name__}")

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
        cache_key = self.get_cache_key(force, item_id, item_type, kwargs, raw, 'c')

        if force:
            self.cache.delete(cache_key)

        if cache_key not in self.cache:
            ce = self.get_item(item_id, raw=True, item_type=item_type)
            children = self._get_children_for_platform_item(ce, raw=raw, **kwargs)
            self.cache.set(cache_key, children, expire=self._object_cache_expiration)
            return children

        return self.cache.get(cache_key)

    def get_children_by_object(self, parent: IEntity) -> List[IEntity]:
        """
        Returns a list of children for an entity

        Args:
            parent: Parent object

        Returns:
            List of children
        """
        return self._get_children_for_platform_item(parent.get_platform_object(), raw=False)

    def get_parent_by_object(self, child: IEntity) -> IEntity:
        """
        Parent of object

        Args:
            child: Child object to find parent for

        Returns:
            Returns parent object
        """
        return self._get_parent_for_platform_item(child.get_platform_object(), raw=False)

    def _get_parent_for_platform_item(self, platform_item: Any, raw: bool = True, **kwargs) -> Any:
        """
        Return the parent item for a given platform_item.

        Args:
            platform_item: Child item
            raw: Return a platform item if True, an idm-tools entity if false
            **kwargs: Additional platform specific parameters

        Returns:
            Parent or None
        """
        item_type, interface = self._get_operation_interface(platform_item)
        if item_type not in [ItemType.EXPERIMENT, ItemType.SIMULATION, ItemType.WORKFLOW_ITEM, ItemType.WorkItem]:
            raise ValueError("Currently only Experiments, Simulations and Work Items support parents")
        obj = getattr(self, interface).get_parent(platform_item, **kwargs)
        if obj is not None:
            parent_item_type, parent_interface = self._get_operation_interface(obj)
            if not raw:
                return getattr(self, parent_interface).to_entity(obj)
        return obj

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

    def get_cache_key(self, force, item_id, item_type, kwargs, raw, prefix='p'):
        if not item_type or item_type not in self.supported_types:
            raise Exception("The provided type is invalid or not supported by this platform...")
        # Create the cache key based on everything we pass to the function
        cache_key = f'{prefix}_{item_id}' + ('r' if raw else 'o') + '_'.join(f"{k}_{v}" for k, v in kwargs.items())
        if force:
            self.cache.delete(cache_key)
        return cache_key

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
            interface = ITEM_TYPE_TO_OBJECT_INTERFACE[key]
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
            interface = ITEM_TYPE_TO_OBJECT_INTERFACE[item.item_type]
            getattr(self, interface).run_item(item)

    @abstractmethod
    def supported_experiment_types(self) -> List[Type]:
        """
        Returns a list of supported experiment types. These types should be either abstract or full classes that have
        been derived from IExperiment

        Returns:
            A list of supported experiment types.
        """
        return [IExperiment]

    @abstractmethod
    def unsupported_experiment_types(self) -> List[Type]:
        """
        Returns a list of experiment types not supported by the platform. These types should be either abstract or full
        classes that have been derived from IExperiment
        
        Returns:
            A list of experiment types not supported by the platform.
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
        """
        Convert an Native Platform Object to an idmtools object

        Args:
            platform_item:  Item to convert
            **kwargs: Optional items to be used in to_entity calls

        Returns:
            IDMTools representation of object
        """
        for src_type, dest_type in self.platform_type_map.items():
            if isinstance(platform_item, src_type):
                interface = ITEM_TYPE_TO_OBJECT_INTERFACE[dest_type]
                return getattr(self, interface).to_entity(platform_item, **kwargs)
        return platform_item

    def flatten_item(self, item: IEntity) -> List[IEntity]:
        """
        Flatten an item: resolve the children until getting to the leaves.
        For example, for an experiment, will return all the simulations.
        For a suite, will return all the simulations contained in the suites experiments.

        Args:
            item: Which item to flatten

        Returns:
            List of leaves

        """
        children = self.get_children(item.uid, item.item_type, force=True)
        if children is None or (isinstance(children, list) and len(children) == 0):
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
        interface = ITEM_TYPE_TO_OBJECT_INTERFACE[item.item_type]
        getattr(self, interface).refresh_status(item)

    def get_files(self, item: IEntity, files: Union[Set[str], List[str]]) -> \
            Union[Dict[str, Dict[str, bytearray]], Dict[str, bytearray]]:
        """
        Get files for a platform entity

        Args:
            item: Item to fetch files for
            files: List of file names to get

        Returns:
            For simulations, this returns a dictionary with filename as key and values being binary data from file or a
            dict.
        
            For experiments, this returns a dictionary with key as sim id and then the values as a dict of the
            simulations described above
        """
        if item.item_type not in self.platform_type_map.values():
            raise UnsupportedPlatformType("The provided type is invalid or not supported by this platform...")
        interface = ITEM_TYPE_TO_OBJECT_INTERFACE[item.item_type]
        return getattr(self, interface).get_assets(item, files)

    def is_task_supported(self, task: 'ITask') -> bool:
        return all([x in self._platform_supports for x in task.platform_requirements])


TPlatform = TypeVar("TPlatform", bound=IPlatform)
TPlatformClass = Type[TPlatform]
