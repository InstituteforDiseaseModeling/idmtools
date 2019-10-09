import ast
import uuid
import typing

from abc import ABCMeta, abstractmethod
from dataclasses import fields
from logging import getLogger
from typing import Any, Dict, List, NoReturn

from idmtools.core.interfaces.ientity import IEntity

if typing.TYPE_CHECKING:
    from idmtools.entities.ianalyzer import TAnalyzerList
    from idmtools.entities.iitem import TItem, TItemList
    import uuid

logger = getLogger(__name__)

CALLER_LIST = ['_create_from_block',    # create platform through Platform Factory
               'fetch',                 # create platform through un-pickle
               'get',                    # create platform through platform spec' get method
               '_main',
               '__newobj__']


class IPlatform(IEntity, metaclass=ABCMeta):
    """
    Interface defining a platform.
    A platform needs to implement basic operation such as:

    - Creating experiment
    - Creating simulation
    - Commissioning
    - File handling
    """

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

    def __post_init__(self) -> None:
        """
        Work to be done after object creation.

        Returns: 
            None
        """
        self.validate_inputs_types()

    @abstractmethod
    def create_items(self, items: 'TItem') -> 'List[uuid]':
        """
        Create items (simulations, experiments, or suites) on the platform.

        Args:
            items: The batch of items to create.

        Returns: 
            List of item IDs created.
        """
        pass

    @abstractmethod
    def run_items(self, items: 'TItemList') -> NoReturn:
        """
        Run the items (sims, exps, suites) on the platform
        Args:
            items: The items to run
        """
        pass

    @abstractmethod
    def send_assets(self, item: 'TItem', **kwargs) -> NoReturn:
        """
        Send the assets for a given item to the platform.

        Args:
            item: The item to process. Expected to have an **assets** attribute containing 
                the collection.
            **kwargs: Extra parameters used by the platform.
        """
        pass

    @abstractmethod
    def refresh_status(self, item) -> NoReturn:
        """
        Populate the platform item and specified item with its status.

        Args:
            item: The item to check status for.
        """
        pass

    @abstractmethod
    def get_item(self, id: 'uuid') -> Any:
        """
        Get an item by its ID. The implementing classes must know how to distinguish
        items of different levels (e.g. simulation, experiment, suite).

        Args:
            id: The ID of the item to obtain.

        Returns: 
            The specified item.
        """
        pass

    # TODO: add doc comments to get_prent/children methods
    @abstractmethod
    def get_parent(self, item: 'TItem') -> 'TItem':
        pass

    @abstractmethod
    def get_children(self, item: 'TItem') -> 'TItemList':
        pass

    def _get_root_items_for_item(self, item: 'TItem') -> 'TItemList':
        children = item.children(refresh=True)
        if children is None:
            items = [item]
        else:
            items = list()
            for child in children:
                items += self._get_root_items_for_item(item=child)
        return items

    def get_root_items(self, items: 'TItemList') -> 'TItemList':
        root_items = []
        for item in items:
            root_items += self._get_root_items_for_item(item=item)
        root_items = list({item.uid: item for item in root_items}.values())  # uniquify
        return root_items

    @abstractmethod
    def get_files(self, item: 'TItem', files: 'List[str]') -> 'Dict[str, bytearray]':
        """
        Obtain specified files related to the given item (an item, a base item).

        Args:
            item: The item to retrieve file data for.
            files: The relative-path files to obtain.

        Returns: 
            A dictionary of file data keyed by file path.

        """
        pass

    @abstractmethod
    def initialize_for_analysis(self, items: 'TItemList', analyzers: 'TAnalyzerList') -> NoReturn:
        """
        Perform any preparation needed before performing analysis on the given items with
        the provided analyzers.

        Args:
            items: A list of items to initialize (base objects).
            analyzers: The analyzers to be applied to the items during analysis.

        Returns:
            None
        """
        pass

    def __repr__(self):
        return f"<Platform {self.__class__.__name__} - id: {self.uid}>"

    def validate_inputs_types(self) -> None:
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
