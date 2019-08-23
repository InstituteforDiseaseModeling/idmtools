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

    # Relative item hierarchy offsets (for relationship arguments)
    SELF = 0
    PARENT = 1
    CHILD = -1

    def __post_init__(self) -> None:
        """
        Got called from Platform creation
        """
        # self.update_from_config()
        if not hasattr(self, '_FACTORY'):
            self.update_from_config()

    @abstractmethod
    def create_objects(self, objects) -> 'List[uuid]':
        """
        Function creating e.g. sims/exps/suites on the platform
        Args:
            objects: The batch of objects to create
        Returns: List of ids created
        """
        pass

    @abstractmethod
    def run_objects(self, objects) -> NoReturn:
        """
        Run the objects (sims, exps, suites) on the platform
        Args:
            objects: The objects to run
        """
        pass

    @abstractmethod
    def send_assets(self, object, **kwargs) -> NoReturn:
        """
        Send the assets for a given object (sim, experiment, suite, etc) to the platform.
        Args:
            object: The object to process. Expected to have an `assets` attribute containing the collection.
            **kwargs: Extra parameters used by the platform
        """
        pass

    @abstractmethod
    def refresh_status(self, object) -> NoReturn:
        """
        Populate the platform object and specified object with its status.
        Args:
            object: The object to check status for
        """
        pass

    @abstractmethod
    def get_object(self, id: 'uuid', level: int) -> Any:
        """
        Get an object by its id and specified hierarchy level
        Args:
            id: the id of the object to obtain
            level: 0 for a base object, > 0 for hierarchical groupings of base objects

        Returns: the specified object

        """
        pass

    @abstractmethod
    def get_objects_by_relationship(self, object, relationship: int) -> list:
        """
        Obtain objects by parent/child relationships relative to another object
        Args:
            object: the reference object
            relationship: The desired object(s) are of this relationship to the provided object

        Returns: a list of objects related to 'object' in the specified way

        """
        pass

    @abstractmethod
    def get_files(self, item: 'TItem', files: 'List[str]') -> 'Dict[str, bytearray]':
        """
        Obtain specified files related to the given object (an Item, a base object)
        Args:
            item: object to retrieve file data for
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
