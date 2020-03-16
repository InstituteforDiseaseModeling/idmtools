# Define our model specific specifications
import typing
from abc import ABC
from logging import getLogger
import pluggy
from idmtools.entities.itask import ITask
from idmtools.registry import PluginSpecification
from idmtools.registry.plugin_specification import PLUGIN_REFERENCE_NAME
from idmtools.registry.utils import load_plugin_map


example_configuration_spec = pluggy.HookspecMarker(PLUGIN_REFERENCE_NAME)
get_task_spec = pluggy.HookspecMarker(PLUGIN_REFERENCE_NAME)
get_task_type_spec = pluggy.HookspecMarker(PLUGIN_REFERENCE_NAME)
example_configuration_impl = pluggy.HookimplMarker(PLUGIN_REFERENCE_NAME)
get_task_impl = pluggy.HookimplMarker(PLUGIN_REFERENCE_NAME)
get_task_type_impl = pluggy.HookimplMarker(PLUGIN_REFERENCE_NAME)
logger = getLogger(__name__)


class TaskSpecification(PluginSpecification, ABC):

    @classmethod
    def get_name(cls) -> str:
        return cls.__name__.replace('TaskSpecification', '').replace("TaskSpec", '').replace('Spec', '')

    @get_task_spec
    def get(self, configuration: dict) -> 'ITask':  # noqa: F821
        """
        Return a new model using the passed in configuration.

        Args:
            configuration: The INI configuration file to use.

        Returns:
            The new model.
        """
        raise NotImplementedError("Plugin did not implement get")

    @get_task_type_spec
    def get_type(self) -> typing.Type['ITask']:  # noqa: F821
        pass


class TaskPlugins:
    def __init__(self) -> None:
        self._plugins = typing.cast(typing.Dict[str, TaskSpecification],
                                    load_plugin_map('idmtools_task', TaskSpecification))

    def get_plugins(self) -> typing.Set[TaskSpecification]:
        return set(self._plugins.values())

    def get_plugin_map(self) -> typing.Dict[str, TaskSpecification]:
        return self._plugins
