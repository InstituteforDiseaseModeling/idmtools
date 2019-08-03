import typing
from abc import ABC

import pluggy


from idmtools.entities import IPlatform
from idmtools.registry.PluginSpecification import PLUGIN_REFERENCE_NAME, PluginSpecification
from idmtools.registry.utils import plugins_loader

example_configuration_spec = pluggy.HookspecMarker(PLUGIN_REFERENCE_NAME)
get_platform_spec = pluggy.HookspecMarker(PLUGIN_REFERENCE_NAME)
get_platform_type_spec = pluggy.HookspecMarker(PLUGIN_REFERENCE_NAME)
example_configuration_impl = pluggy.HookimplMarker(PLUGIN_REFERENCE_NAME)
get_platform_impl = pluggy.HookimplMarker(PLUGIN_REFERENCE_NAME)
get_platform_type_impl = pluggy.HookimplMarker(PLUGIN_REFERENCE_NAME)


# Define our platform specific specifications

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

    @staticmethod
    @get_platform_type_spec
    def get_type() -> typing.Type[IPlatform]:
        pass


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