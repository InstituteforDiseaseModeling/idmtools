# Define our platform specific specifications
import typing
from abc import ABC
from logging import getLogger

import pluggy

from idmtools.entities.iplatform import IPlatform
from idmtools.registry import PluginSpecification
from idmtools.registry.plugin_specification import PLUGIN_REFERENCE_NAME
from idmtools.registry.utils import load_plugin_map

example_configuration_spec = pluggy.HookspecMarker(PLUGIN_REFERENCE_NAME)
get_platform_spec = pluggy.HookspecMarker(PLUGIN_REFERENCE_NAME)
get_platform_type_spec = pluggy.HookspecMarker(PLUGIN_REFERENCE_NAME)
example_configuration_impl = pluggy.HookimplMarker(PLUGIN_REFERENCE_NAME)
get_platform_impl = pluggy.HookimplMarker(PLUGIN_REFERENCE_NAME)
get_platform_type_impl = pluggy.HookimplMarker(PLUGIN_REFERENCE_NAME)
logger = getLogger(__name__)


class PlatformSpecification(PluginSpecification, ABC):

    @classmethod
    def get_name(cls, strip_all: bool = True) -> str:
        """
        Get name of plugin. By default we remove the PlatformSpecification portion.
        Args:
            strip_all: When true, PlatformSpecification is stripped from name. When false only Specification is Stripped

        Returns:

        """
        if strip_all:
            ret = cls.__name__.replace("PlatformSpecification", '')
        else:
            ret = cls.__name__.replace('Specification', '')
        return ret

    @example_configuration_spec
    def example_configuration(self):
        """
        Example configuration for the platform. This is useful in help or error messages.

        Returns:
        """
        raise NotImplementedError("Plugin did not implement example_configuration")

    @get_platform_spec
    def get(self, configuration: dict) -> IPlatform:
        """
        Return a new platform using the passed in configuration.

        Args:
            configuration: The INI configuration file to use.

        Returns:
            The new platform.
        """
        raise NotImplementedError("Plugin did not implement get")

    @get_platform_type_spec
    def get_type(self) -> typing.Type[IPlatform]:
        pass


class PlatformPlugins:
    def __init__(self, strip_all: bool = True) -> None:
        """
        Initialize the Platform Registry. When strip all is false, the full plugin name will be used for names in map

        Args:
            strip_all: Whether to strip common parts of name from plugins in plugin map
        """
        self._plugins = typing.cast(typing.Dict[str, PlatformSpecification],
                                    load_plugin_map('idmtools_platform', PlatformSpecification, strip_all))

    def get_plugins(self) -> typing.Set[PlatformSpecification]:
        return set(self._plugins.values())

    def get_plugin_map(self) -> typing.Dict[str, PlatformSpecification]:
        return self._plugins
