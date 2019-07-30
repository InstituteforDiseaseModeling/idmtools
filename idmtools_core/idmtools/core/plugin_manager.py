import functools
import glob
import importlib
import inspect
import sys
from logging import getLogger, DEBUG
from os.path import join, isfile, sep
from typing import List, Any, Type, Optional, Set

import pluggy


PLUGIN_REFERENCE_NAME = 'idmtools_plugins'

# Common Spec hooks
get_description_spec = pluggy.HookspecMarker(PLUGIN_REFERENCE_NAME)
get_description_impl = pluggy.HookimplMarker(PLUGIN_REFERENCE_NAME)

logger = getLogger(__name__)


class PluginSpecification:
    """
    This class is a base generic definition for all classes
    """

    @classmethod
    def get_name(cls) -> str:
        """
        We can override if we need but the best option for more plugins is just use their class name as the plugin name
        Returns:
            (str) Name of Plugin
        """
        return cls.__name__

    @staticmethod
    @get_description_spec
    def get_description() -> str:
        """
        A brief description of the plugin and its functionality

        Returns:

        """
        raise NotImplementedError("The plugin did not implement a description!")


def list_rindex(lst, item):
    """
    Find first place item occurs in list, but starting at end of list.
    Return index of item in list, or -1 if item not found in the list.
    """
    i_max = len(lst)
    i_limit = -i_max
    i = -1
    while i > i_limit:
        if lst[i] == item:
            return i_max + i
        i -= 1
    return -1


def is_a_plugin_of_type(value, plugin_specification: Type[PluginSpecification]) -> bool:
    """
    Determine if a value if a plugin specification of type plugin_specification

    Args:
        value: Value to inspect
        plugin_specification: Plugin specification to check against

    Returns:
        (bool) True if the plugin is of a subclass of PluginSpecification, else False
    """
    return inspect.isclass(value) and issubclass(value, plugin_specification) and \
           not inspect.isabstract(value) and value is not plugin_specification


def plugins_loader(entry_points_name: str, plugin_specification: Type[PluginSpecification],
                   libraries: Optional[List[Any]] = None) -> Set[PluginSpecification]:
    """
    Loads all the plugins of type *plugin_specification* from entry-point name. We also support loading plugins
    through a list of strs representing the paths to modules containing plugins

    Args:
        entry_points_name: Entry point name for plugins
        plugin_specification: Plugin specification to load
        libraries: List of module objects or paths to load

    Returns:
        (Set[PluginSpecification]): All the plugins of type X
    """
    manager = pluggy.PluginManager(PLUGIN_REFERENCE_NAME)
    manager.add_hookspecs(plugin_specification)
    manager.load_setuptools_entrypoints(entry_points_name)

    if libraries:
        load_plugins_from_module_list(libraries, manager, plugin_specification)

    manager.check_pending()
    return manager.get_plugins()


def load_plugins_from_module_list(libraries: List[Any], manager: pluggy.PluginManager,
                                  plugin_specification: Type[PluginSpecification]):
    """
    Discovers plugins from a list of modules specified as strings and registers them with the specified plugin manager

    Args:
        libraries: List of libraries to discover plugins from
        manager: Plugin manager to register the plugins with
        plugin_specification: The type of plugin to search for

    Returns:
        None. The plugins are registered directly on the manager
    """
    plugins = []
    for library in libraries:
        plugins.extend(
            [p for p in discover_plugins_from(library, plugin_specification) if p not in manager.get_plugins()])
    # if we found plugins, load them all
    if plugins:
        # map(manager.register, plugins)
        for pl in plugins:
            manager.register(pl)
    else:
        logger.warn("No plugins found of type %s", PluginSpecification.__name__)


def load_each_module_from(base_path: str, paths: List[str]):
    """
    Loadd all python files in a specific path(except __init__.py). Used in dynamic search of plugins

    TODO: Add error handling in case of guard against library layout changes in future
    Args:
        base_path:
        paths:

    Returns:

    """
    libraries = []
    logger.debug(f'Base Path: {base_path}')
    for path in paths:
        modules = glob.glob(join(join(base_path, path.replace('.', sep), "**/**.py")), recursive=True)
        for f in modules:
            if isfile(f) and not f.endswith('__init__.py'):
                parts = f.split(sep)
                mod_name = sep.join(parts[(list_rindex(parts, path.split('.')[0])):])[:-3].replace(sep, '.')
                logger.debug(f'Importing module {mod_name}')
                libraries.append(importlib.import_module(mod_name))
    return libraries


@functools.lru_cache(maxsize=32)
def discover_plugins_from(library: Any, plugin_specification: Type[PluginSpecification]) -> \
        List[Type[PluginSpecification]]:
    """
    Search a library obj for plugins of type plugin_specification.

    Currently it detects module and classes. In the future support for strs will be added
    Args:
        library: Library object to discover plugins from
        plugin_specification: Specification to search for

    Returns:
        List[Type[PluginSpecification]]: List of Plugins
    """

    plugins = []
    # check if the item is a module
    if inspect.ismodule(library):
        if logger.isEnabledFor(DEBUG):
            logger.debug('Attempting to load library as a module: %s', library.__name__)
        for k, v in library.__dict__.items():
            if k[:2] != '__' and is_a_plugin_of_type(v, plugin_specification):
                if logger.isEnabledFor(DEBUG):
                    logger.debug('Adding class %s from %s as a plugin', v.__name__, library.__name__)
                plugins.append(v)
    # or maybe a plugin object
    elif is_a_plugin_of_type(library, plugin_specification):
        if logger.isEnabledFor(DEBUG):
            logger.debug('Adding class %s as a plugin', library.__name__)
        plugins.append(library)
    else:
        logger.warn('Could not determine the the type of library specified by %s', str(library))
    return plugins
