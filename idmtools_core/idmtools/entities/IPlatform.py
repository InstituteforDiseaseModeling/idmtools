import uuid
from abc import ABCMeta, abstractmethod
from dataclasses import fields

import typing
from logging import getLogger, DEBUG

from idmtools.config import IdmConfigParser
from idmtools.core.interfaces.IEntity import IEntity

if typing.TYPE_CHECKING:
    from idmtools.core.types import TExperiment, TSimulation, TSimulationBatch
    from typing import List, Dict, Any


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
    def create_objects(self, objects) -> 'List[Any]':
        """
        Function creating e.g. sims/exps/suites on the platform
        Args:
            objects: The batch of objects to create
        Returns:
            List of ids created
        """
        pass

    @abstractmethod
    def run_objects(self, objects):
        """
        Run the objects (sims, exps, suites) on the platform
        Args:
            objects: The objects to run
        """
        pass

    @abstractmethod
    def send_assets(self, object, **kwargs) -> None:
        """
        Send the assets for a given object (sim, experiment, suite, etc) to the platform.
        Args:
            object: The object to process. Expected to have an `assets` attribute containing the collection.
            **kwargs: Extra parameters used by the platform
        """
        pass

    @abstractmethod
    def refresh_status(self, object) -> None:
        """
        Populate the platform object and any child objects with status.
        Args:
            obj: The object (Item) to check status for
        """
        pass

    @abstractmethod
    def get_object(self, id, level):
        pass

    @abstractmethod
    def get_objects_by_relationship(self, object, relationship):
        pass

    @abstractmethod
    def get_files(self, item, files: 'List[str]') -> 'Dict[str, bytearray]':
        pass

    @abstractmethod
    def initialize_for_analysis(self, items, analyzers) -> None:
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

        # find, load and get settings from config file. Return with the correct data types
        if logger.isEnabledFor(DEBUG):
            logger.debug(f'Loading Platform config from {self.__class__.__name__.replace("Platform", "")}')
        field_config = IdmConfigParser.retrieve_settings(self.__class__.__name__.replace("Platform", ""), field_type)

        # display not used fields from config
        field_config_not_used = set(field_config.keys()) - set(field_name)
        if len(field_config_not_used) > 0:
            field_config_not_used = [" - {} = {}".format(fn, field_config[fn]) for fn in field_config_not_used]
            logger.warning(f"[{self.__class__.__name__}]: the following Config Settings are not used:")
            logger.warning("\n".join(field_config_not_used))
            print(f"[{self.__class__.__name__}]: the following Config Settings are not used:")
            print("\n".join(field_config_not_used))

        # update attr based on priority: #1 Code, #2 INI, #3 Default
        for fn in set(field_config.keys()).intersection(set(field_name)):
            if field_value[fn] != field_default[fn]:
                setattr(self, fn, field_value[fn])
            elif field_config[fn] != field_value[fn]:
                setattr(self, fn, field_config[fn])
