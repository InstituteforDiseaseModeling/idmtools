"""
Here we define the Platform interface.

IPlatform is responsible for all the communication to our platform and translation from idmtools objects to platform specific objects and vice versa.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import os
import copy
import warnings
from abc import ABCMeta
from dataclasses import dataclass
from dataclasses import fields, field
from functools import partial
from os import PathLike
import pandas as pd
from pathlib import PureWindowsPath, PurePath
from itertools import groupby
from logging import getLogger, DEBUG
from typing import Dict, List, NoReturn, Type, TypeVar, Any, Union, Tuple, Set, Iterator, Callable, Optional

from idmtools import IdmConfigParser
from idmtools.core import CacheEnabled, UnknownItemException, EntityContainer, UnsupportedPlatformType
from idmtools.core.enums import ItemType, EntityStatus
from idmtools.core.interfaces.ientity import IEntity
from idmtools.core.interfaces.iitem import IItem
from idmtools.core.interfaces.irunnable_entity import IRunnableEntity
from idmtools.entities.experiment import Experiment
from idmtools.core.id_file import read_id_file
from idmtools.entities.iplatform_default import IPlatformDefault
from idmtools.entities.iplatform_ops.iplatform_asset_collection_operations import IPlatformAssetCollectionOperations
from idmtools.entities.iplatform_ops.iplatform_experiment_operations import IPlatformExperimentOperations
from idmtools.entities.iplatform_ops.iplatform_simulation_operations import IPlatformSimulationOperations
from idmtools.entities.iplatform_ops.iplatform_suite_operations import IPlatformSuiteOperations
from idmtools.entities.iplatform_ops.iplatform_workflowitem_operations import IPlatformWorkflowItemOperations
from idmtools.entities.itask import ITask
from idmtools.entities.iworkflow_item import IWorkflowItem
from idmtools.entities.platform_requirements import PlatformRequirements
from idmtools.entities.relation_type import RelationType
from idmtools.entities.simulation import Simulation
from idmtools.entities.suite import Suite
from idmtools.assets.asset_collection import AssetCollection
from idmtools.services.platforms import PlatformPersistService
from idmtools.utils.caller import get_caller
from idmtools.utils.entities import validate_user_inputs_against_dataclass

logger = getLogger(__name__)
user_logger = getLogger('user')

CALLER_LIST = ['_create_from_block',  # create platform through Platform Factory
               'fetch',  # create platform through un-pickle
               'get',  # create platform through platform spec' get method
               '__newobj__',  # create platform through copy.deepcopy
               '_main']  # create platform through analyzer manager

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
    Experiment: ItemType.EXPERIMENT,
    Simulation: ItemType.SIMULATION,
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
    #: Maps the platform types to idmtools types
    platform_type_map: Dict[Type, ItemType] = field(default=None, repr=False, init=False)
    _object_cache_expiration: 'int' = field(default=60, repr=False, init=False)

    supported_types: Set[ItemType] = field(default_factory=lambda: set(), repr=False, init=False)
    _platform_supports: List[PlatformRequirements] = field(default_factory=list, repr=False, init=False)
    _platform_defaults: List[IPlatformDefault] = field(default_factory=list)

    _experiments: IPlatformExperimentOperations = field(default=None, repr=False, init=False, compare=False)
    _simulations: IPlatformSimulationOperations = field(default=None, repr=False, init=False, compare=False)
    _suites: IPlatformSuiteOperations = field(default=None, repr=False, init=False, compare=False)
    _workflow_items: IPlatformWorkflowItemOperations = field(default=None, repr=False, init=False, compare=False)
    _assets: IPlatformAssetCollectionOperations = field(default=None, repr=False, init=False, compare=False)
    #: Controls what platform should do we re-running experiments by default
    _regather_assets_on_modify: bool = field(default=False, repr=False, init=False, compare=False)
    # store the config block used to create platform
    _config_block: str = field(default=None)
    #: Defines the path to common assets
    _common_asset_path: str = field(default="Assets", repr=True, init=False, compare=False)

    def __new__(cls, *args, **kwargs):
        """
        Create a new object.

        Args:
            args: User inputs.
            kwargs: User inputs.

        Returns:
            The object created.

        Raises:
            ValueError - If the platform was not created as expected.
        """
        # Check the caller
        caller = get_caller()

        # Action based on the caller
        if caller not in CALLER_LIST:
            warnings.warn(
                "Please use Factory to create Platform! For example: \n    platform = Platform('COMPS', **kwargs)")
        return super().__new__(cls)

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

    def _get_platform_item(self, item_id: str, item_type: ItemType, **kwargs) -> Any:
        """
        Get an item by its ID.

        The implementing classes must know how to distinguish items of different levels (e.g. simulation, experiment, suite).

        Args:
            item_id: The ID of the item to retrieve.
            item_type: The type of object to retrieve.

        Returns:
            The specified item found on the platform or None.

        Raises:
            ValueError: If the item type is not supported
        """
        if item_type not in self.platform_type_map.values():
            raise ValueError(f"Unsupported Item Type. {self.__class__.__name__} only supports "
                             f"{self.platform_type_map.values()}")
        interface = ITEM_TYPE_TO_OBJECT_INTERFACE[item_type]
        return getattr(self, interface).get(item_id, **kwargs)

    def get_item(self, item_id: str, item_type: ItemType = None, force: bool = False, raw: bool = False,
                 **kwargs) -> Union[Experiment, Suite, Simulation, IWorkflowItem, AssetCollection, None]:
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

        Raises:
            ValueError: If the item type is not supported
            UnknownItemException: If the item type is not found on platform
        """
        if not item_type or item_type not in self.platform_type_map.values():
            raise ValueError("The provided type is invalid or not supported by this platform...")

        cache_key = self.get_cache_key(force, item_id, item_type, kwargs, raw, 'r' if raw else 'o')

        # If force -> delete in the cache
        if force:
            if logger.isEnabledFor(DEBUG):
                logger.debug(f"Removing {cache_key} from cache")
            self.cache.delete(cache_key)

        # If we cannot find the object in the cache -> retrieve depending on the type
        if cache_key not in self.cache:
            if logger.isEnabledFor(DEBUG):
                logger.debug(f"Retrieve item {item_id} of type {item_type}")
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
            return_object.platform = self

        return return_object

    def _get_children_for_platform_item(self, item: Any, raw: bool = True, **kwargs) -> List[Any]:
        """
        Returns the children for a platform object.

        For example, A COMPS Experiment or Simulation.

        The children can either be returns as native platform objects or as idmtools objects.

        Args:
            item: Item to fetch children for
            raw: When true, return the native platform representation of  the children, otherwise return the idmtools
                implementation
            **kwargs:

        Returns:
            Children of platform object
        """
        item_type, interface = self._get_operation_interface(item)
        if item_type in [ItemType.EXPERIMENT, ItemType.SUITE]:
            children = getattr(self, ITEM_TYPE_TO_OBJECT_INTERFACE[item_type]).get_children(item, **kwargs)
        else:
            return []
        if not raw:
            ret = []
            for e in children:
                n = self._convert_platform_item_to_entity(e, **kwargs)
                if n._platform_object is None:
                    n._platform_object = e
                ret.append(n)
            return EntityContainer(ret)
        else:
            return children

    def _get_operation_interface(self, item: Any) -> Tuple[ItemType, str]:
        """
        Get the base item type and the interface string for said item.

        For example, on COMPSPlatform, if you passed a COMPSExperiment object, the function would return ItemType.Experiment, _experiments


        Args:
            item: Item to look up

        Returns:
            Tuple with the Base item type and the string path to the interface

        Raises:
            ValueError: If the item 's interface cannot be found
        """
        # check both base types and platform specs
        for interface_type_mapping in [STANDARD_TYPE_TO_INTERFACE, self.platform_type_map]:
            for interface, item_type in interface_type_mapping.items():
                if isinstance(item, interface):
                    return item_type, ITEM_TYPE_TO_OBJECT_INTERFACE[item_type]
        raise ValueError(f"{self.__class__.__name__} has no mapping for {item.__class__.__name__}")

    def get_children(self, item_id: str, item_type: ItemType,
                     force: bool = False, raw: bool = False, item: Any = None, **kwargs) -> Any:
        """
        Retrieve the children of a given object.

        Args:
            item_id: The ID of the object for which we want the children.
            force: If True, force the object fetching from the platform.
            raw: Return either an |IT_s| object or a platform object.
            item_type: Pass the type of the object for quicker retrieval.
            item: optional platform or idm item to use instead of loading

        Returns:
            The children of the object or None.
        """
        cache_key = self.get_cache_key(force, item_id, item_type, kwargs, raw, 'c')

        if force:
            self.cache.delete(cache_key)

        if cache_key not in self.cache:
            ce = item or self.get_item(item_id, raw=raw, item_type=item_type)
            ce.platform = self
            kwargs['parent'] = ce
            children = self._get_children_for_platform_item(ce.get_platform_object(), raw=raw, **kwargs)
            self.cache.set(cache_key, children, expire=self._object_cache_expiration)
            return children

        return self.cache.get(cache_key)

    def get_children_by_object(self, parent: IEntity) -> List[IEntity]:
        """
        Returns a list of children for an entity.

        Args:
            parent: Parent object

        Returns:
            List of children
        """
        return self._get_children_for_platform_item(parent.get_platform_object(), raw=False)

    def get_parent_by_object(self, child: IEntity) -> IEntity:
        """
        Parent of object.

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
            raw: Return a platform item if True, an idmtools entity if false
            **kwargs: Additional platform specific parameters

        Returns:
            Parent or None
        """
        item_type, interface = self._get_operation_interface(platform_item)
        if item_type not in [ItemType.EXPERIMENT, ItemType.SIMULATION, ItemType.WORKFLOW_ITEM]:
            raise ValueError("Currently only Experiments, Simulations and Work Items support parents")
        obj = getattr(self, interface).get_parent(platform_item, **kwargs)
        if obj is not None:
            parent_item_type, parent_interface = self._get_operation_interface(obj)
            if not raw:
                return getattr(self, parent_interface).to_entity(obj)
        return obj

    def get_parent(self, item_id: str, item_type: ItemType = None, force: bool = False,
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
        """
        Get cache key for an item.

        Args:
            force: Should we force the load
            item_id: Item id
            item_type: Item type
            kwargs: Kwargs
            raw: Should we use raw storage?
            prefix: Prefix for the item

        Returns:
            Cache Key
        """
        if not item_type or item_type not in self.supported_types:
            raise Exception("The provided type is invalid or not supported by this platform...")
        # Create the cache key based on everything we pass to the function
        cache_key = f'{prefix}_{item_id}' + ('r' if raw else 'o') + '_'.join(f"{k}_{v}" for k, v in kwargs.items())
        if force:
            self.cache.delete(cache_key)
        return cache_key

    def create_items(self, items: Union[List[IEntity], IEntity], **kwargs) -> List[IEntity]:
        """
        Create items (simulations, experiments, or suites) on the platform.

        The function will batch the items based on type and call the self._create_batch for creation.

        Args:
            items: The list of items to create.
            kwargs: Extra arguments
        Returns:
            List of item IDs created.
        """
        if isinstance(items, IEntity):
            items = [items]
        if not isinstance(items, Iterator):
            self._is_item_list_supported(items)

        result = []
        for key, group in groupby(items, lambda x: x.item_type):
            result.extend(self._create_items_of_type(group, key, **kwargs))
        return result

    def _create_items_of_type(self, items: Iterator[IEntity], item_type: ItemType, **kwargs):
        """
        Creates items of specific type using batches.

        Args:
            items: Items to create
            item_type: Item type to create

        Returns:
            Items created
        """
        interface = ITEM_TYPE_TO_OBJECT_INTERFACE[item_type]
        ni = getattr(self, interface).batch_create(items, **kwargs)
        return ni

    def _is_item_list_supported(self, items: List[IEntity]):
        """
        Checks if all items in a list are supported by the platform.

        Args:
            items: Items to verify

        Returns:
            True if items supported, false otherwise

        Raises:
            ValueError: If the item type is not supported
        """
        for item in items:
            if item.item_type not in self.platform_type_map.values():
                raise ValueError(
                    f'Unable to create items of type: {item.item_type} for platform: {self.__class__.__name__}')

    def run_items(self, items: Union[IEntity, List[IEntity]], **kwargs):
        """
        Run items on the platform.

        Args:
            items: Items to run

        Returns:
            None
        """
        if isinstance(items, IEntity):
            items = [items]
        self._is_item_list_supported(items)

        for item in items:
            item.platform = self
            interface = ITEM_TYPE_TO_OBJECT_INTERFACE[item.item_type]
            getattr(self, interface).run_item(item, **kwargs)

    def __repr__(self):
        """Platform as string."""
        return f"<Platform {self.__class__.__name__} - id: {self.uid}>"

    def _convert_platform_item_to_entity(self, platform_item: Any, **kwargs) -> IEntity:
        """
        Convert a Native Platform Object to an idmtools object.

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

    def validate_item_for_analysis(self, item: object, analyze_failed_items=False):
        """
        Check if item is valid for analysis.

        Args:
            item: Which item to flatten
            analyze_failed_items: bool

        Returns: bool

        """
        result = False
        if item.succeeded:
            result = True
        else:
            if analyze_failed_items and item.status == EntityStatus.FAILED:
                result = True

        return result

    def flatten_item(self, item: object, **kwargs) -> List[object]:
        """
        Flatten an item: resolve the children until getting to the leaves.

        For example, for an experiment, will return all the simulations.
        For a suite, will return all the simulations contained in the suites experiments.

        Args:
            item: Which item to flatten
            kwargs: extra parameters

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
        if item.platform is None:
            item.platform = self
        getattr(self, interface).refresh_status(item)

    def get_files(self, item: IEntity, files: Union[Set[str], List[str]], output: str = None, **kwargs) -> \
            Union[Dict[str, Dict[str, bytearray]], Dict[str, bytearray]]:
        """
        Get files for a platform entity.

        Args:
            item: Item to fetch files for
            files: List of file names to get
            output: save files to
            kwargs: Platform arguments

        Returns:
            For simulations, this returns a dictionary with filename as key and values being binary data from file or a
            dict.

            For experiments, this returns a dictionary with key as sim id and then the values as a dict of the
            simulations described above
        """
        if item.item_type not in self.platform_type_map.values():
            raise UnsupportedPlatformType("The provided type is invalid or not supported by this platform...")
        interface = ITEM_TYPE_TO_OBJECT_INTERFACE[item.item_type]
        ret = getattr(self, interface).get_assets(item, files, **kwargs)

        if output:
            if item.item_type not in (ItemType.SIMULATION, ItemType.WORKFLOW_ITEM):
                user_logger.info("Currently 'output' only supports Simulation and WorkItem!")
            else:
                for ofi, ofc in ret.items():
                    file_path = os.path.join(output, str(item.uid), ofi)
                    parent_path = os.path.dirname(file_path)
                    if not os.path.exists(parent_path):
                        os.makedirs(parent_path)

                    with open(file_path, 'wb') as outfile:
                        outfile.write(ofc)

        return ret

    def get_files_by_id(self, item_id: str, item_type: ItemType, files: Union[Set[str], List[str]],
                        output: str = None) -> \
            Union[Dict[str, Dict[str, bytearray]], Dict[str, bytearray]]:
        """
        Get files by item id (str).

        Args:
            item_id: COMPS Item, say, Simulation Id or WorkItem Id
            item_type: Item Type
            files: List of files to retrieve
            output: save files to

        Returns: dict with key/value: file_name/file_content
        """
        idm_item = self.get_item(item_id, item_type, raw=False)
        return self.get_files(idm_item, files, output)

    def are_requirements_met(self, requirements: Union[PlatformRequirements, Set[PlatformRequirements]]) -> bool:
        """
        Does the platform support the list of requirements.

        Args:
            requirements: Requirements should be a list of PlatformRequirements or a single PlatformRequirements

        Returns:
            True if all the requirements are supported
        """
        if isinstance(requirements, PlatformRequirements):
            requirements = [requirements]
        return all([x in self._platform_supports for x in requirements])

    def is_task_supported(self, task: ITask) -> bool:
        """
        Is a task supported on this platform.

        This depends on the task properly setting its requirements. See :py:attr:`idmtools.entities.itask.ITask.platform_requirements` and
        :py:class:`idmtools.entities.platform_requirements.PlatformRequirements`

        Args:
            task: Task to check support of

        Returns:
            True if the task is supported, False otherwise.
        """
        return self.are_requirements_met(task.platform_requirements)

    def __wait_till_callback(
            self, item: Union[Experiment, IWorkflowItem, Suite],
            callback: Union[partial, Callable[[Union[Experiment, IWorkflowItem, Suite]], bool]],
            timeout: int = 60 * 60 * 24,
            refresh_interval: int = 5
    ):
        """
        Runs a loop until a timeout is met where the item's status is refreshed. A callback is then called with the items as the arguments and if the returns is true, we stop waiting.

        Args:
            item: Item to monitor
            callback: Callback to determine if item is done. It should return true is item is complete
            timeout: Timeout for waiting. Defaults to 24 hours
            refresh_interval: Refresh the status how often

        Returns:
            None

        Raises:
            TimeoutError: If a timeout occurs

        See Also:
            :meth:`idmtools.entities.iplatform.IPlatform.wait_till_done_progress`
            :meth:`idmtools.entities.iplatform.IPlatform.__wait_until_done_progress_callback`
            :meth:`idmtools.entities.iplatform.IPlatform.wait_till_done`
        """
        import time
        start_time = time.time()
        while time.time() - start_time < timeout:
            if logger.isEnabledFor(DEBUG):
                logger.debug("Refreshing simulation status")
            self.refresh_status(item)
            if callback(item):
                return
            time.sleep(refresh_interval)
        raise TimeoutError(f"Timeout of {timeout} seconds exceeded")

    def wait_till_done(self, item: IRunnableEntity, timeout: int = 60 * 60 * 24,
                       refresh_interval: int = 5, progress: bool = True):
        """
        Wait for the experiment to be done.

        Args:
            item: Experiment/Workitem to wait on
            refresh_interval: How long to wait between polling.
            timeout: How long to wait before failing.
            progress: Should we display progress

        See Also:
            :meth:`idmtools.entities.iplatform.IPlatform.wait_till_done_progress`
            :meth:`idmtools.entities.iplatform.IPlatform.__wait_until_done_progress_callback`
            :meth:`idmtools.entities.iplatform.IPlatform.__wait_till_callback`
        """
        if progress:
            self.wait_till_done_progress(item, timeout, refresh_interval)
        else:
            self.__wait_till_callback(item, lambda e: e.done, timeout, refresh_interval)

    @staticmethod
    def __wait_until_done_progress_callback(item: Union[Experiment, IWorkflowItem], progress_bar: 'tqdm',  # noqa: F821
                                            child_attribute: str = 'simulations',
                                            done_states: List[EntityStatus] = None,
                                            failed_warning: Dict[str, bool] = False) -> bool:
        """
        A callback for progress bar(when an item has children) and checking if an item has completed execution.

        This is mainly meant for aggregate types where the status is from the children.

        Args:
            item: Item to monitor
            progress_bar:
            child_attribute: What is the name of the child attribute. For examples, if item was an Experiment, the
                child_attribute would be 'simulations'
            done_states: What states are considered done
            failed_warning: Used to track if we have warned user of failure. We use dict to pass by refernce since we cannot do that with a bool

        Returns:
            True is item has completed execution

        See Also:
            :meth:`idmtools.entities.iplatform.IPlatform.wait_till_done_progress`
            :meth:`idmtools.entities.iplatform.IPlatform.wait_till_done`
            :meth:`idmtools.entities.iplatform.IPlatform.__wait_till_callback`
        """
        # ensure we have done states. Default to failed or SUCCEEDED
        if done_states is None:
            done_states = [EntityStatus.FAILED, EntityStatus.SUCCEEDED]
        # if we do not have a progress bar, return items state
        if child_attribute is None:
            if isinstance(item, IWorkflowItem):
                if item.status in done_states:
                    if progress_bar:
                        progress_bar.update(1)
                        progress_bar.close()
                    return True
                return False
            else:
                return item.done

        # if we do have a progress bar, update it
        done = 0
        # iterate over the children
        for child in getattr(item, child_attribute):
            # if the item is an experiment, use the status
            if isinstance(item, Experiment) and child.status in done_states:
                done += 1
            # otherwise use the done attribute
            elif isinstance(item, Suite) and child.done:
                done += 1
        # check if we need to update the progress bar
        if hasattr(progress_bar, 'last_print_n') and done > progress_bar.last_print_n:
            progress_bar.update(done - progress_bar.last_print_n)
        # Alert user to failing simulations so they can stop execution if wanted
        if isinstance(item, Experiment) and item.any_failed and not failed_warning['failed_warning']:
            user_logger.warning(f"The Experiment {item.uid} has failed simulations. Check Experiment in platform")
            failed_warning['failed_warning'] = True
        return item.done

    def wait_till_done_progress(self, item: IRunnableEntity, timeout: int = 60 * 60 * 24, refresh_interval: int = 5,
                                wait_progress_desc: str = None):
        """
        Wait on an item to complete with progress bar.

        Args:
            item: Item to monitor
            timeout: Timeout on waiting
            refresh_interval: How often to refresh
            wait_progress_desc: Wait Progress Description

        Returns:
            None

        See Also:
            :meth:`idmtools.entities.iplatform.IPlatform.__wait_until_done_progress_callback`
            :meth:`idmtools.entities.iplatform.IPlatform.wait_till_done`
            :meth:`idmtools.entities.iplatform.IPlatform.__wait_till_callback`
        """
        # set prog to list
        prog = []
        # check that the user has not disable progress bars
        child_attribute = None
        if not IdmConfigParser.is_progress_bar_disabled():
            from tqdm import tqdm
            if isinstance(item, Experiment):
                prog = tqdm([], total=len(item.simulations),
                            desc=wait_progress_desc if wait_progress_desc else f"Waiting on Experiment {item.name} to Finish running",
                            unit="simulation")
                child_attribute = 'simulations'
            elif isinstance(item, Suite):
                prog = tqdm([], total=len(item.experiments),
                            desc=wait_progress_desc if wait_progress_desc else f"Waiting on Suite {item.name} to Finish running",
                            unit="experiment")
                child_attribute = 'experiments'
            elif isinstance(item, IWorkflowItem):
                prog = tqdm([], total=1,
                            desc=wait_progress_desc if wait_progress_desc else f"Waiting on WorkItem {item.name}",
                            unit="workitem")
        else:
            child_attribute = None

        failed_warning = dict(failed_warning=False)
        self.__wait_till_callback(
            item,
            partial(self.__wait_until_done_progress_callback, progress_bar=prog, child_attribute=child_attribute,
                    failed_warning=failed_warning),
            timeout,
            refresh_interval
        )

    def get_related_items(self, item: IWorkflowItem, relation_type: RelationType) -> Dict[str, Dict[str, str]]:
        """
        Retrieve all related objects.

        Args:
            item: SSMTWorkItem
            relation_type: Depends or Create

        Returns: dict with key the object type
        """
        if item.item_type != ItemType.WORKFLOW_ITEM:
            raise UnsupportedPlatformType("The provided type is invalid or not supported by this platform...")
        interface = ITEM_TYPE_TO_OBJECT_INTERFACE[item.item_type]
        return getattr(self, interface).get_related_items(item, relation_type)

    def __enter__(self):
        """
        Enable our platform to work on contexts.

        Returns:
            Platform
        """
        from idmtools.core.context import set_current_platform
        set_current_platform(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Enable our platform to work on contexts.

        Args:
            exc_type: Type of exception type
            exc_val:Value
            exc_tb: Traceback

        Returns:
            None
        """
        from idmtools.core.context import remove_current_platform
        remove_current_platform()

    def is_regather_assets_on_modify(self) -> bool:
        """
        Return default behaviour for platform when rerunning experiment and gathering assets.

        Returns:
            True or false
        """
        return self._regather_assets_on_modify

    def is_windows_platform(self, item: IEntity = None) -> bool:
        """
        Returns is the target platform is a windows system.
        """
        return self.are_requirements_met(PlatformRequirements.WINDOWS)

    @property
    def common_asset_path(self):
        """
        Return the path to common assets stored on the platform.

        Returns:
            Common Asset Path
        """
        return self._common_asset_path

    @common_asset_path.setter
    def common_asset_path(self, value):
        """
        Set path to common assets stored on the platform. This path should be in defined in relation to individual items(simulations, workflow items).

        For example, on COMPS, we would set "Assets"

        Args:
            value: Path to use for common path

        Returns:
            None
        """
        if not isinstance(value, property):
            logger.warning("Cannot set common asset path")

    def join_path(self, *args) -> str:
        """
        Join path using platform rules.

        Args:
            *args:List of paths to join

        Returns:
            Joined path as string
        """
        if len(args) < 2:
            raise ValueError("at least two items required to join")
        if self.is_windows_platform():
            return str(PureWindowsPath(*args))
        else:
            return str(PurePath(*args))

    def id_from_file(self, filename: str):
        """
        Load just the id portion of an id file.

        Args:
            filename: Filename

        Returns:
            Item id laoded from file
        """
        item_id, item_type, platform_block, extra_args = read_id_file(filename)
        return item_id

    def get_item_from_id_file(self, id_filename: Union[PathLike, str], item_type: Optional[ItemType] = None) -> IEntity:
        """
        Load an item from an id file. This ignores the platform in the file.

        Args:
            id_filename: Filename to load
            item_type: Optional item type

        Returns:
            Item from id file.
        """
        item_id, file_item_type, platform_block, extra_args = read_id_file(id_filename)
        return self.get_item(item_id, item_type if item_type else ItemType[file_item_type.upper()])

    def get_defaults_by_type(self, default_type: Type) -> List[IPlatformDefault]:
        """
        Returns any platform defaults for specific types.
        Args:
            default_type: Default type

        Returns:
            List of default of that type
        """
        return [x for x in self._platform_defaults if isinstance(x, default_type)]

    def create_sim_directory_map(self, item_id: str, item_type: ItemType) -> Dict:
        """
        Build simulation working directory mapping.
        Args:
            item_id: Entity id
            item_type: ItemType
        Returns:
            Dict of simulation id as key and working dir as value
        """
        interface = ITEM_TYPE_TO_OBJECT_INTERFACE[item_type]
        return getattr(self, interface).create_sim_directory_map(item_id)

    def create_sim_directory_df(self, exp_id: str, include_tags: bool = True) -> pd.DataFrame:
        """
        Build simulation working directory mapping.
        Args:
            exp_id: experiment id
            include_tags: True/False
        Returns:
            DataFrame
        """
        tag_df = None
        if include_tags:
            tags_list = []
            sims = self.get_children(exp_id, ItemType.EXPERIMENT)
            for sim in sims:
                tags = copy.deepcopy(sim.tags)
                tags["simid"] = sim.id
                tags_list.append(tags)
            tag_df = pd.DataFrame(tags_list)

        dir_map = self.create_sim_directory_map(exp_id, ItemType.EXPERIMENT)

        dir_list = [dict(simid=sim_id, outpath=str(path)) for sim_id, path in dir_map.items()]
        dir_df = pd.DataFrame(dir_list)

        if tag_df is not None and len(tag_df) > 0:
            result_df = pd.merge(left=tag_df, right=dir_df, on='simid')
        else:
            result_df = dir_df

        return result_df

    def save_sim_directory_df_to_csv(self, exp_id: str, include_tags: bool = True,
                                     output: str = os.getcwd(), save_header=False, file_name: str = None) -> None:
        """
        Save simulation directory df to csv file.
        Args:
            exp_id: experiment id
            include_tags: True/False
            output: output directory
            save_header: True/False
            file_name: user csv file name
        Returns:
            None
        """
        df = self.create_sim_directory_df(exp_id, include_tags=include_tags)
        try:
            os.mkdir(output)
        except OSError:
            pass

        if file_name is None:
            file_name = f'{exp_id}.csv'
        df.to_csv(os.path.join(output, file_name), header=save_header, index=False)


TPlatform = TypeVar("TPlatform", bound=IPlatform)
TPlatformClass = Type[TPlatform]
