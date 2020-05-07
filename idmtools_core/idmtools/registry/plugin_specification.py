from dataclasses import dataclass
from logging import getLogger
import pluggy
from typing import List, Union

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

    @staticmethod
    def read_templates_from_json_stream(s) -> List['ProjectTemplate']:
        """
        Read Project Template from stream

        Args:
            s: Stream where json data resides

        Returns:

        """
        import json
        data = json.loads(s.read().decode())
        ret = list()
        if isinstance(data, list):
            for item in data:
                ret.append(ProjectTemplate(**item))
        else:
            ret.append(ProjectTemplate(**data))
        return ret


class PluginSpecification:
    """
    Base class for all plugins.
    """

    @classmethod
    def get_name(cls, strip_all: bool = True) -> str:
        """
        Get the name of the plugin. Although it can be overridden, the best practice is to use the class
        name as the plugin name.

        Returns:
            The name of the plugin as a string.
        """
        if strip_all:
            return cls.__name__.replace("Specification", "")
        else:
            return cls.__name__

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
