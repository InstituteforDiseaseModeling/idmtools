import uuid
from abc import ABCMeta, abstractmethod, ABC
from dataclasses import fields

import pluggy
import typing

from idmtools.core import IEntity
from idmtools.config import IdmConfigParser
from idmtools.core.plugin_manager import PluginSpecification, PLUGIN_REFERENCE_NAME, plugins_loader

if typing.TYPE_CHECKING:
    from idmtools.core.types import TExperiment, TSimulation, TSimulationBatch
    from typing import List, Dict, Any


class IPlatform(IEntity, metaclass=ABCMeta):
    """
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
    def create_experiment(self, experiment: 'TExperiment') -> None:
        """
        Function creating an experiment on the platform.
        Args:
            experiment: The experiment to create
        """
        pass

    @abstractmethod
    def create_simulations(self, simulation_batch: 'TSimulationBatch') -> 'List[Any]':
        """
        Function creating experiments simulations on the platform for a given experiment.
        Args:
            simulation_batch: The batch of simulations to create
        Returns:
            List of ids created
        """
        pass

    @abstractmethod
    def run_simulations(self, experiment: 'TExperiment') -> None:
        """
        Run the simulations for a given experiment on the platform
        Args:
            experiment: The experiment to run
        """
        pass

    @abstractmethod
    def send_assets_for_experiment(self, experiment: 'TExperiment', **kwargs) -> None:
        """
        Send the assets for a given experiment to the platform.
        Args:
            experiment: The experiment to process. Expected to have an `assets` attribute containing the collection.
            **kwargs: Extra parameters used by the platform
        """
        pass

    @abstractmethod
    def send_assets_for_simulation(self, simulation: 'TSimulation', **kwargs) -> None:
        """
        Send the assets for a given simulation to the platform.
        Args:
            simulation: The simulation to process. Expected to have an `assets` attribute containing the collection.
            **kwargs: Extra parameters used by the platform
        """
        pass

    @abstractmethod
    def refresh_experiment_status(self, experiment: 'TExperiment') -> None:
        """
        Populate the experiment and its simulations with status.
        Args:
            experiment: The experiment to check status for
        """
        pass

    @abstractmethod
    def restore_simulations(self, experiment: 'TExperiment') -> None:
        """
        Populate the experiment with the associated simulations.
        Args:
            experiment: The experiment to populate
        """
        pass

    @abstractmethod
    def get_assets_for_simulation(self, simulation: 'TSimulation', output_files: 'List[str]') -> 'Dict[str, bytearray]':
        pass

    @abstractmethod
    def retrieve_experiment(self, experiment_id: 'uuid') -> 'TExperiment':
        pass

    def __repr__(self):
        return f"<Platform {self.__class__.__name__} - id: {self.uid}>"

    def update_from_config(self) -> None:
        """
        Get INI config values and update platform values by the priority rules:
            #1 Code, #2 INI config, #2 default
        Returns: None
        """
        # retrieve field values, default values and types
        fds = fields(self)
        field_name = [f.name for f in fields(self)]
        field_default = {f.name: f.default for f in fds}
        field_value = {f.name: getattr(self, f.name) for f in fds}
        field_type = {f.name: f.type for f in fds}

        # find, load and get settings from config file. Return with the correct data types
        field_config = IdmConfigParser.retrieve_settings(self.__class__.__name__, field_type)

        # display not used fields from config
        field_config_not_used = set(field_config.keys()) - set(field_name)
        if len(field_config_not_used) > 0:
            field_config_not_used = [" - {} = {}".format(fn, field_config[fn]) for fn in field_config_not_used]
            print(f"[{self.__class__.__name__}]: the following Config Settings are not used:")
            print("\n".join(field_config_not_used))

        # update attr based on priority: #1 Code, #2 INI, #3 Default
        for fn in set(field_config.keys()).intersection(set(field_name)):
            if field_value[fn] != field_default[fn]:
                setattr(self, fn, field_value[fn])
            elif field_config[fn] != field_value[fn]:
                setattr(self, fn, field_config[fn])


# Define our platform specific specifications
example_configuration_spec = pluggy.HookspecMarker(PLUGIN_REFERENCE_NAME)
get_platform_spec = pluggy.HookspecMarker(PLUGIN_REFERENCE_NAME)

example_configuration_impl = pluggy.HookimplMarker(PLUGIN_REFERENCE_NAME)
get_platform_impl = pluggy.HookimplMarker(PLUGIN_REFERENCE_NAME)


class PlatformSpecification(PluginSpecification, ABC):

    @classmethod
    def get_name(cls) -> str:
        return cls.__name__.replace('Platform', '').replace('Specification', '')

    @staticmethod
    @example_configuration_spec
    def example_configuration():
        """
        Example configuration for platform. This is useful in help or error messages
        Returns:

        """
        raise NotImplementedError("Plugin did not implement example_configuration")

    @staticmethod
    @get_platform_spec
    def get(configuration: dict) -> IPlatform:
        """
        Factor that should return a new platform using the passed in configuration
        Args:
            configuration:

        Returns:

        """
        raise NotImplementedError("Plugin did not implement get")


class PlatformPlugins:
    def __init__(self) -> None:
        self._plugins = typing.cast(
            typing.Set[PlatformSpecification],
            plugins_loader('idmtools_platform', PlatformSpecification)
        )

    def get_plugins(self) -> typing.Set[PlatformSpecification]:
        return self._plugins

    def get_plugin_map(self) -> typing.Dict[str, PlatformSpecification]:
        return {plugin.get_name(): plugin for plugin in self._plugins}
