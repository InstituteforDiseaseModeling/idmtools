# Define our model specific specifications
import typing
from abc import ABC
from logging import getLogger

import pluggy

from idmtools.registry import PluginSpecification
from idmtools.registry.plugin_specification import PLUGIN_REFERENCE_NAME
from idmtools.registry.utils import load_plugin_map

example_configuration_spec = pluggy.HookspecMarker(PLUGIN_REFERENCE_NAME)
get_model_spec = pluggy.HookspecMarker(PLUGIN_REFERENCE_NAME)
get_model_type_spec = pluggy.HookspecMarker(PLUGIN_REFERENCE_NAME)
example_configuration_impl = pluggy.HookimplMarker(PLUGIN_REFERENCE_NAME)
get_model_impl = pluggy.HookimplMarker(PLUGIN_REFERENCE_NAME)
get_model_type_impl = pluggy.HookimplMarker(PLUGIN_REFERENCE_NAME)
logger = getLogger(__name__)


class ExperimentPluginSpecification(PluginSpecification, ABC):

    @classmethod
    def get_name(cls, strip_all: bool = True) -> str:
        """
        Get name of plugin. By default we remove the PlatformSpecification portion.
        Args:
            strip_all: When true, ExperimentPluginSpecification and ExperimentPluginSpec is stripped from name.
             When false only  Specification and Spec is Stripped

        Returns:

        """
        if strip_all:
            ret = cls.__name__.replace('ExperimentPluginSpecification', '').replace("ExperimentPluginSpec", '').replace(
                'Spec', '')
        else:
            ret = cls.__name__.replace('Specification', '').replace('Spec', '')
        return ret

    @get_model_spec
    def get(self, configuration: dict) -> 'Experiment':  # noqa: F821
        """
        Return a new model using the passed in configuration.

        Args:
            configuration: The INI configuration file to use.

        Returns:
            The new model.
        """
        raise NotImplementedError("Plugin did not implement get")

    @get_model_type_spec
    def get_type(self) -> typing.Type['Experiment']:  # noqa: F821
        pass


class ExperimentPlugins:
    def __init__(self, strip_all: bool = True) -> None:
        """
        Initialize the Experiment Registry. When strip all is false, the full plugin name will be used for names in map

        Args:
            strip_all: Whether to strip common parts of name from plugins in plugin map
        """
        self._plugins = typing.cast(typing.Dict[str, ExperimentPluginSpecification],
                                    load_plugin_map('idmtools_experiment', ExperimentPluginSpecification, strip_all))

    def get_plugins(self) -> typing.Set[ExperimentPluginSpecification]:
        return set(self._plugins.values())

    def get_plugin_map(self) -> typing.Dict[str, ExperimentPluginSpecification]:
        return self._plugins
