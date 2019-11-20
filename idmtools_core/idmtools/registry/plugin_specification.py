from dataclasses import dataclass
from logging import getLogger
import pluggy
from typing import Dict, List, Union

PLUGIN_REFERENCE_NAME = 'idmtools_plugins'
get_description_spec = pluggy.HookspecMarker(PLUGIN_REFERENCE_NAME)
get_description_impl = pluggy.HookimplMarker(PLUGIN_REFERENCE_NAME)
logger = getLogger(__name__)


@dataclass
class ProjectTemplate:
    name: str
    url: Union[str, List[str]]
    description: str = None
    info: str = None


class PluginSpecification:
    """
    Base class for all plugins.
    """

    @classmethod
    def get_name(cls) -> str:
        """
        Get the name of the plugin. Although it can be overridden, the best practice is to use the class
        name as the plugin name.

        Returns:
            The name of the plugin as a string.
        """
        return cls.__name__.replace("Specification", "")

    @get_description_spec
    def get_description(self) -> str:
        """
        Get a brief description of the plugin and its functionality.

        Returns:
            The plugin description.
        """
        raise NotImplementedError("The plugin did not implement a description!")

    def get_project_templates(self) -> List[ProjectTemplate]:
        """
        Returns a list of project templates related to the a plugin
        Returns:

        """
        return list()
