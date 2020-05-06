from typing import Dict, Set
from idmtools.registry import PluginSpecification
from idmtools.registry.experiment_specification import ExperimentPlugins


class MasterPluginRegistry:
    def __init__(self) -> None:
        from idmtools.registry.platform_specification import PlatformPlugins
        from idmtools.registry.task_specification import TaskPlugins
        self._plugin_map = PlatformPlugins(strip_all=False).get_plugin_map()
        self._plugin_map.update(TaskPlugins(strip_all=False).get_plugin_map())
        self._plugin_map.update(ExperimentPlugins(strip_all=False).get_plugin_map())

    def get_plugin_map(self) -> Dict[str, PluginSpecification]:
        return self._plugin_map

    def get_plugins(self) -> Set[PluginSpecification]:
        return set(self._plugin_map.values())
