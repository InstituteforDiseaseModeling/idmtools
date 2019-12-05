
# Define our platform specific specifications
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
    @classmethod
    def get_name(cls) -> str:
        return cls.__name__.replace("CLISpecification", "")

    @get_platform_cli_spec
    def get(configuration: dict) -> IPlatformCLI:
        """
        Factor that should return a new platform using the passed in configuration
        Args:
            configuration:

        Returns:

        """
        raise NotImplementedError("Plugin did not implement get")

    @get_additional_commands_spec
    def get_additional_commands(self) -> NoReturn:
        raise NotImplementedError("Plugin did not implement get_additional_commands")


class PlatformCLIPlugins:
    def __init__(self) -> None:
        self._plugins = cast(Dict[str, PlatformCLISpecification],
                             load_plugin_map('idmtools_platform_cli', PlatformCLISpecification))

    def get_plugins(self) -> Set[PlatformCLISpecification]:
        return set(self._plugins.values())

    def get_plugin_map(self) -> Dict[str, PlatformCLISpecification]:
        return self._plugins
