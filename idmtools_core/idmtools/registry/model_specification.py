# Define our model specific specifications
import typing
from abc import ABC
from logging import getLogger
import pluggy
from idmtools.registry import PluginSpecification
from idmtools.registry.plugin_specification import PLUGIN_REFERENCE_NAME
from idmtools.registry.utils import load_plugin_map
from idmtools.utils.decorators import SingletonDecorator

example_configuration_spec = pluggy.HookspecMarker(PLUGIN_REFERENCE_NAME)
get_model_spec = pluggy.HookspecMarker(PLUGIN_REFERENCE_NAME)
get_model_type_spec = pluggy.HookspecMarker(PLUGIN_REFERENCE_NAME)
example_configuration_impl = pluggy.HookimplMarker(PLUGIN_REFERENCE_NAME)
get_model_impl = pluggy.HookimplMarker(PLUGIN_REFERENCE_NAME)
get_model_type_impl = pluggy.HookimplMarker(PLUGIN_REFERENCE_NAME)
logger = getLogger(__name__)


class ModelSpecification(PluginSpecification, ABC):

    @classmethod
    def get_name(cls) -> str:
        return cls.__name__.replace('ModelSpecification', '').replace("ModelSpec", '').replace('Spec', '')

    @get_model_spec
    def get(self, configuration: dict) -> 'IModel':  # noqa: F821
        """
        Return a new model using the passed in configuration.

        Args:
            configuration: The INI configuration file to use.

        Returns:
            The new model.
        """
        raise NotImplementedError("Plugin did not implement get")

    @get_model_type_spec
    def get_type(self) -> typing.Type['IModel']:  # noqa: F821
        pass


class ModelPlugins:
    def __init__(self) -> None:
        self._plugins = typing.cast(typing.Dict[str, ModelSpecification],
                                    load_plugin_map('idmtools_model', ModelSpecification))

    def get_plugins(self) -> typing.Set[ModelSpecification]:
        return set(self._plugins.values())

    def get_plugin_map(self) -> typing.Dict[str, ModelSpecification]:
        return self._plugins


ModelPlugins = SingletonDecorator(ModelPlugins)
