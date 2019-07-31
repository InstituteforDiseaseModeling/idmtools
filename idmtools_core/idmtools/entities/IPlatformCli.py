
# Define our platform specific specifications
from abc import ABC, abstractmethod
from typing import NoReturn, Dict, Set, cast
import pluggy
import typing

from idmtools.core.plugin_manager import PLUGIN_REFERENCE_NAME, PluginSpecification, plugins_loader

get_platform_cli_spec = pluggy.HookspecMarker(PLUGIN_REFERENCE_NAME)
get_additional_commands = pluggy.HookspecMarker(PLUGIN_REFERENCE_NAME)


class IPlatformCLI(ABC):

    @abstractmethod
    def get_experiment_status(self, *args, **kwargs) -> NoReturn:
        """
        Fetch the status based on the argument for current platform

        Args:
            *args:
            **kwargs:

        Returns:

        """
        pass

    @abstractmethod
    def get_simulation_status(self, *args, **kwargs) -> NoReturn:
        """
        Fetch the status based on the argument for current platform

        Args:
            *args:
            **kwargs:

        Returns:

        """
        pass

    @abstractmethod
    def get_platform_information(self) -> dict:
        pass


class PlatformCLISpecification(PluginSpecification, ABC):

    @staticmethod
    @get_platform_cli_spec
    def get(configuration: dict) -> IPlatformCLI:
        """
        Factor that should return a new platform using the passed in configuration
        Args:
            configuration:

        Returns:

        """
        raise NotImplementedError("Plugin did not implement get")

    @staticmethod
    @get_additional_commands
    def get_additional_commands() -> NoReturn:
        raise NotImplementedError("Plugin did not implement get_additional_commands")


class PlatformCLIPlugins:
    def __init__(self) -> None:
        self._plugins = cast(
            Set[PlatformCLISpecification],
            plugins_loader('idmtools_platform_cli', PlatformCLISpecification)
        )

    def get_plugins(self) -> Set[PlatformCLISpecification]:
        return self._plugins

    def get_plugin_map(self) -> Dict[str, PlatformCLISpecification]:
        return {plugin.get_name(): plugin for plugin in self._plugins}