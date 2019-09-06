import typing

from abc import ABCMeta, abstractmethod
from dataclasses import fields

from idmtools.config import IdmConfigParser
from idmtools.core.interfaces.IEntity import IEntity
from logging import getLogger, DEBUG
from typing import Any, Dict, List, NoReturn

if typing.TYPE_CHECKING:
    from idmtools.core.types import TAnalyzerList, TItem, TItemList
    import uuid

logger = getLogger(__name__)


class IPlatform(IEntity, metaclass=ABCMeta):
    """
    Interface defining a platform.
    Interface defining a platform.
    A platform needs to implement basic operation such as:
    - Creating experiment
    - Creating simulation
    - Commissioning
    - File handling
    """

    def __post_init__(self) -> None:
        """
        Got called from Platform creation
        """
        # self.update_from_config()
        if not hasattr(self, '_FACTORY'):
            self.update_from_config()

    @abstractmethod
    def create_items(self, items: 'TItem') -> 'List[uuid]':
        """
        Function creating e.g. sims/exps/suites on the platform
        Args:
            items: The batch of items to create
        Returns: List of ids created
        """
        pass

    @abstractmethod
    def run_items(self, items: 'TItem') -> NoReturn:
        """
        Run the items (sims, exps, suites) on the platform
        Args:
            items: The items to run
        """
        pass

    @abstractmethod
    def send_assets(self, item: 'TItem', **kwargs) -> NoReturn:
        """
        Send the assets for a given item (sim, experiment, suite, etc) to the platform.
        Args:
            item: The item to process. Expected to have an `assets` attribute containing the collection.
            **kwargs: Extra parameters used by the platform
        """
        pass

    @abstractmethod
    def refresh_status(self, item) -> NoReturn:
        """
        Populate the platform item and specified item with its status.
        Args:
            item: The item to check status for
        """
        pass

    @abstractmethod
    def get_item(self, id: 'uuid') -> Any:
        """
        Get an item by its id. The implementing classes must know how to distinguish
        items of different levels (e.g. simulation, experiment, ...)
        Args:
            id: the id of the item to obtain

        Returns: the specified item
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
        Obtain specified files related to the given item (an Item, a base item)
        Args:
            item: item to retrieve file data for
            files: relative-path files to obtain

        Returns: a dict of file-path-keyed file data

        """
        pass

    @abstractmethod
    def initialize_for_analysis(self, items: 'TItemList', analyzers: 'TAnalyzerList') -> NoReturn:
        """
        Perform any pre-analysis steps needed before performing analysis on the given items with
        the provided analyzers
        Args:
            items: a list of items to initialize (base objects)
            analyzers: analyzers to be applied to the items during analysis

        Returns:

        """
        pass

    def __repr__(self):
        return f"<Platform {self.__class__.__name__} - id: {self.uid}>"

    def update_from_config(self) -> None:
        """
        Get INI config values and update platform values by the priority rules:
        #1 Code
        #2 INI config
        #2 default

        Returns: None
        """
        # retrieve field values, default values and types
        fds = fields(self)
        field_name = [f.name for f in fields(self)]
        field_default = {f.name: f.default for f in fds}
        field_value = {f.name: getattr(self, f.name) for f in fds}
        field_type = {f.name: f.type for f in fds}

        block = self.__class__.__name__.replace("Platform", "")

        # find, load and get settings from config file. Return with the correct data types
        if logger.isEnabledFor(DEBUG):
            logger.debug(f'Loading Platform config from {block}')
        field_config = IdmConfigParser.retrieve_settings(block, field_type)

        # display not used fields from config
        field_config_not_used = set(field_config.keys()) - set(field_name)
        if 'type' in field_config_not_used:
            field_config_not_used.remove('type')
        if len(field_config_not_used) > 0:
            field_config_not_used = [" - {} = {}".format(fn, field_config[fn]) for fn in field_config_not_used]
            logger.warning(f"[{block}]: the following Config Settings are not used:")
            logger.warning("\n".join(field_config_not_used))
            print(f"[{block}]: the following Config Settings are not used:")
            print("\n".join(field_config_not_used))

        # update attr based on priority: #1 Code, #2 INI, #3 Default
        for fn in set(field_config.keys()).intersection(set(field_name)):
            if field_value[fn] != field_default[fn]:
                setattr(self, fn, field_value[fn])
            elif field_config[fn] != field_value[fn]:
                setattr(self, fn, field_config[fn])

        IdmConfigParser.display_config_block_details(block)
