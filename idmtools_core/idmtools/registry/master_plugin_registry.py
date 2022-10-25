"""
Registry to aggregate all plugins to one place.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from typing import Dict, Set
from idmtools.registry import PluginSpecification
from idmtools.registry.experiment_specification import ExperimentPlugins
from idmtools.utils.decorators import SingletonMixin


class MasterPluginRegistry(SingletonMixin):
    """
    MasterPluginRegistry indexes all type of plugins into one class.

    Notes:
        TODO - Rename this class
    """

    def __init__(self) -> None:
        """
        Initialize Master registry.
        """
        from idmtools.registry.platform_specification import PlatformPlugins
        from idmtools.registry.task_specification import TaskPlugins
        self._plugin_map = PlatformPlugins(strip_all=False).get_plugin_map()
        self._plugin_map.update(TaskPlugins(strip_all=False).get_plugin_map())
        self._plugin_map.update(ExperimentPlugins(strip_all=False).get_plugin_map())
        try:
            from idmtools_cli.iplatform_cli import PlatformCLIPlugins
            self._plugin_map.update(PlatformCLIPlugins(strip_all=False).get_plugin_map())
        except ImportError:
            pass

    def get_plugin_map(self) -> Dict[str, PluginSpecification]:
        """
        Get plugin map.

        Returns:
            Plugin map
        """
        return self._plugin_map

    def get_plugins(self) -> Set[PluginSpecification]:
        """
        Get Plugins map.

        Returns:
            The full plugin map
        """
        return set(self._plugin_map.values())
