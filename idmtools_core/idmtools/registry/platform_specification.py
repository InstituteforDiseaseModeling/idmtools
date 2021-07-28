"""
PlatformSpecification provided definition for the platform plugin specification, hooks, and plugin manager.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
# Define our platform specific specifications
import typing
from abc import ABC
from logging import getLogger, DEBUG
import pluggy
from idmtools.registry import PluginSpecification
from idmtools.registry.plugin_specification import PLUGIN_REFERENCE_NAME
from idmtools.registry.utils import load_plugin_map
from idmtools.utils.decorators import SingletonMixin

if typing.TYPE_CHECKING:
    from idmtools.entities.iplatform import IPlatform
example_configuration_spec = pluggy.HookspecMarker(PLUGIN_REFERENCE_NAME)
get_platform_spec = pluggy.HookspecMarker(PLUGIN_REFERENCE_NAME)
get_platform_type_spec = pluggy.HookspecMarker(PLUGIN_REFERENCE_NAME)
example_configuration_impl = pluggy.HookimplMarker(PLUGIN_REFERENCE_NAME)
get_platform_impl = pluggy.HookimplMarker(PLUGIN_REFERENCE_NAME)
get_platform_type_impl = pluggy.HookimplMarker(PLUGIN_REFERENCE_NAME)
logger = getLogger(__name__)


class PlatformSpecification(PluginSpecification, ABC):
    """
    PlatformSpecification for Platform Plugins.
    """

    @classmethod
    def get_name(cls, strip_all: bool = True) -> str:
        """
        Get name of plugin. By default we remove the PlatformSpecification portion.

        Args:
            strip_all: When true, PlatformSpecification is stripped from name. When false only Specification is Stripped

        Returns:
            Name of plugin
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
            Example configuration
        """
        raise NotImplementedError("Plugin did not implement example_configuration")

    @get_platform_spec
    def get(self, configuration: dict) -> 'IPlatform':
        """
        Return a new platform using the passed in configuration.

        Args:
            configuration: The INI configuration file to use.

        Returns:
            The new platform.
        """
        raise NotImplementedError("Plugin did not implement get")

    @get_platform_type_spec
    def get_type(self) -> typing.Type['IPlatform']:
        """
        Get type of the Platform type.
        """
        pass

    def get_configuration_aliases(self) -> typing.Dict[str, typing.Dict]:
        """
        Get a list of configuration aliases for the platform.

        A configuration alias should be in the form of "name" -> "Spec, Config Options Dict" where name is the alias the user will use, and the config options is a dictionary of config options to be passed to the item
        Returns:

        """
        return {}


class PlatformPlugins(SingletonMixin):
    """
    PlatformPlugin registry.
    """

    def __init__(self, strip_all: bool = True) -> None:
        """
        Initialize the Platform Registry. When strip all is false, the full plugin name will be used for names in map.

        Args:
            strip_all: Whether to strip common parts of name from plugins in plugin map
        """
        self._plugins = typing.cast(typing.Dict[str, PlatformSpecification],
                                    load_plugin_map('idmtools_platform', PlatformSpecification, strip_all))
        self._aliases: typing.Dict[str, typing.Tuple[PlatformSpecification, typing.Dict]] = dict()
        for _name, spec in self._plugins.items():
            for alias, details in spec.get_configuration_aliases().items():
                if alias.upper() in self._aliases or alias.upper() in self._plugins:
                    logger.debug(f"Conflicting alias found: {alias.upper()} from {spec.get_name()}")
                if logger.isEnabledFor(DEBUG):
                    logger.debug(f"Found Platform Configuration Alias: {alias}")
                self._aliases[alias.upper()] = (spec, details)

    def get_plugins(self) -> typing.Set[PlatformSpecification]:
        """
        Get platform plugins.

        Returns:
            Platform plugins
        """
        return set(self._plugins.values())

    def get_aliases(self) -> typing.Dict[str, typing.Tuple[PlatformSpecification, typing.Dict]]:
        """
        Get Platform Configuration Aliases for Platform Plugin.

        Returns:
            Platform CConfiguration Aliases
        """
        return self._aliases

    def get_plugin_map(self) -> typing.Dict[str, PlatformSpecification]:
        """
        Get plugin map for Platform Plugins.

        Returns:
            Plugin map
        """
        return self._plugins
