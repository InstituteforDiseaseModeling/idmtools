"""Define our platform specific specifications.

This is a specific specification to illuminate a command CLI between platforms for interacting with
experiment/simulations
"""
#
from abc import ABC, abstractmethod
from typing import NoReturn, Dict, Set, cast, Optional, List, Tuple
import pluggy
from idmtools.registry.plugin_specification import PLUGIN_REFERENCE_NAME, PluginSpecification
from idmtools.registry.utils import load_plugin_map

get_platform_cli_spec = pluggy.HookspecMarker(PLUGIN_REFERENCE_NAME)
get_additional_commands_spec = pluggy.HookspecMarker(PLUGIN_REFERENCE_NAME)
get_platform_cli_impl = pluggy.HookimplMarker(PLUGIN_REFERENCE_NAME)
get_additional_commands_impl = pluggy.HookimplMarker(PLUGIN_REFERENCE_NAME)


class IPlatformCLI(ABC):
    """The Base PLatformCLI definition. It is mostly abstract classes around fetching info from a platform."""

    @abstractmethod
    def get_experiment_status(self, id: Optional[str], tags: Optional[List[Tuple[str, str]]]) -> NoReturn:
        """
        Get experiment status from a platform.

        Args:
            id: Optional ID to search for
            tags: Optional tags to filter for as well

        Returns:
            None
        """
        pass

    @abstractmethod
    def get_simulation_status(self, id: Optional[str], experiment_id: Optional[str], status: Optional[str],
                              tags: Optional[List[Tuple[str, str]]]) -> NoReturn:
        """
        Get simulation status.

        Args:
            id: Optional simulation id
            experiment_id: Optional experiment id
            status: Status to filter for
            tags: Tags to filter for

        Returns:
            None
        """
        pass

    @abstractmethod
    def get_platform_information(self) -> dict:
        """
        Get any platform relevant information.

        Returns:
            Str containing platform info
        """
        pass


class PlatformCLISpecification(PluginSpecification, ABC):
    """Defines the Platform CLI Plugin Base."""
    @classmethod
    def get_name(cls, strip_all: bool = True) -> str:
        """
        Get name of plugin. By default we remove the CLISpecification portion.

        Args:
            strip_all: When true, CLISpecification is stripped from name. When false only Specification is Stripped

        Returns:
            None
        """
        if strip_all:
            ret = cls.__name__.replace("CLISpecification", '')
        else:
            ret = cls.__name__.replace('Specification', '')
        return ret

    @get_platform_cli_spec
    def get(self, configuration: dict) -> IPlatformCLI:
        """
        Factor that should return a new platform using the passed in configuration.

        Args:
            configuration:

        Returns:
            None

        Raises:
            NotImplementedError
        """
        raise NotImplementedError("Plugin did not implement get")

    @get_additional_commands_spec
    def get_additional_commands(self) -> NoReturn:
        """
        Get any additional commands defined by the platform CLI.

        Returns:
            None

        Raises:
            NotImplementedError
        """
        raise NotImplementedError("Plugin did not implement get_additional_commands")


class PlatformCLIPlugins:
    """Platform CLI Plugin Manager. Loads all the plugins."""
    def __init__(self, strip_all: bool = True) -> None:
        """
        Creates our plugin index.

        Args:
            strip_all: Formatting option for plugin names in registry
        """
        self._plugins = cast(Dict[str, PlatformCLISpecification],
                             load_plugin_map('idmtools_platform_cli', PlatformCLISpecification, strip_all))

    def get_plugins(self) -> Set[PlatformCLISpecification]:
        """
        Get plugins in the manager.

        Returns:
            List of plugin specs
        """
        return set(self._plugins.values())

    def get_plugin_map(self) -> Dict[str, PlatformCLISpecification]:
        """
        Get the plugin map.

        Returns:
            Plugin Dict with name of plugin -> plugin cli spec
        """
        return self._plugins
