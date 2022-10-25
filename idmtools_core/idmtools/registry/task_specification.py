"""
TaskSpecification provided definition for the experiment plugin specification, hooks, and plugin manager.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
# Define our model specific specifications
import typing
from abc import ABC
from logging import getLogger
import pluggy
from idmtools.entities.itask import ITask
from idmtools.registry import PluginSpecification
from idmtools.registry.plugin_specification import PLUGIN_REFERENCE_NAME
from idmtools.registry.utils import load_plugin_map
from idmtools.utils.decorators import SingletonMixin

example_configuration_spec = pluggy.HookspecMarker(PLUGIN_REFERENCE_NAME)
get_task_spec = pluggy.HookspecMarker(PLUGIN_REFERENCE_NAME)
get_task_type_spec = pluggy.HookspecMarker(PLUGIN_REFERENCE_NAME)
example_configuration_impl = pluggy.HookimplMarker(PLUGIN_REFERENCE_NAME)
get_task_impl = pluggy.HookimplMarker(PLUGIN_REFERENCE_NAME)
get_task_type_impl = pluggy.HookimplMarker(PLUGIN_REFERENCE_NAME)
logger = getLogger(__name__)


class TaskSpecification(PluginSpecification, ABC):
    """
    TaskSpecification is spec for Task plugins.
    """

    @classmethod
    def get_name(cls, strip_all: bool = True) -> str:
        """
        Get name of plugin. By default we remove the PlatformSpecification portion.

        Args:
            strip_all: When true, TaskSpecification and TaskSpec is stripped from name. When false only
            Specification and Spec is Stripped

        Returns:
            Name of plugin
        """
        if strip_all:
            ret = cls.__name__.replace('TaskSpecification', '').replace("TaskSpec", '').replace('Spec', '')
        else:
            ret = cls.__name__.replace('Specification', '').replace('Spec', '')
        return ret

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
        """
        Get task type.

        Returns:
            Task type
        """
        pass


class TaskPlugins(SingletonMixin):
    """
    TaskPlugins acts as a registry for Task Plugins.
    """

    def __init__(self, strip_all: bool = True) -> None:
        """
        Initialize the Task Registry. When strip all is false, the full plugin name will be used for names in map.

        Args:
            strip_all: Whether to strip common parts of name from plugins in plugin map
        """
        self._plugins = typing.cast(typing.Dict[str, TaskSpecification],
                                    load_plugin_map('idmtools_task', TaskSpecification, strip_all))

    def get_plugins(self) -> typing.Set[TaskSpecification]:
        """
        Get plugins for Tasks.

        Returns:
            Plugins
        """
        return set(self._plugins.values())

    def get_plugin_map(self) -> typing.Dict[str, TaskSpecification]:
        """
        Get a map of task plugins.

        Returns:
            Task plugin map
        """
        return self._plugins
