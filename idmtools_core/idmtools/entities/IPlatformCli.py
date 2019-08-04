
# Define our platform specific specifications
from abc import ABC, abstractmethod
from typing import NoReturn, Dict, Set, cast, Optional, List, Tuple
import pluggy

from idmtools.registry.PluginSpecification import PLUGIN_REFERENCE_NAME, PluginSpecification
from idmtools.registry.utils import plugins_loader

get_platform_cli_spec = pluggy.HookspecMarker(PLUGIN_REFERENCE_NAME)
get_additional_commands = pluggy.HookspecMarker(PLUGIN_REFERENCE_NAME)


class IPlatformCLI(ABC):

    @abstractmethod
    def get_experiment_status(self, id: Optional[str], tags: Optional[List[Tuple[str, str]]]) -> NoReturn:
        """

        Args:
            id:
            tags:

        Returns:

        """
        pass

    @abstractmethod
    def get_simulation_status(self, id: Optional[str], experiment_id: Optional[str], status: Optional[str],
                              tags: Optional[List[Tuple[str, str]]]) -> NoReturn:
        """

        Args:
            id:
            experiment_id:
            status:
            tags:

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
        pl = plugins_loader('idmtools_platform_cli', PlatformCLISpecification)
        self._plugins = cast(Set[PlatformCLISpecification], pl)

    def get_plugins(self) -> Set[PlatformCLISpecification]:
        return self._plugins

    def get_plugin_map(self) -> Dict[str, PlatformCLISpecification]:
        return {plugin.get_name(): plugin for plugin in self._plugins}
