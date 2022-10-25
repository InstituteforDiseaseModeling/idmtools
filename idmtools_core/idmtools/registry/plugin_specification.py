"""
Defines our base plugin definition and specifications.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from dataclasses import dataclass
from logging import getLogger
import pluggy
from typing import List, Union, Dict

PLUGIN_REFERENCE_NAME = 'idmtools_plugins'
get_description_spec = pluggy.HookspecMarker(PLUGIN_REFERENCE_NAME)
get_description_impl = pluggy.HookimplMarker(PLUGIN_REFERENCE_NAME)
logger = getLogger(__name__)


@dataclass
class ProjectTemplate:
    """
    Defines a ProjectTemplate that plugins can define.
    """
    name: str
    url: Union[str, List[str]]
    description: str = None
    info: str = None

    @staticmethod
    def read_templates_from_json_stream(s) -> List['ProjectTemplate']:
        """
        Read Project Template from stream.

        Args:
            s: Stream where json data resides

        Returns:
            Templates loaded from json
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
        Get the name of the plugin. Although it can be overridden, the best practice is to use the class name as the plugin name.

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
        Returns a list of project templates related to the a plugin.

        Returns:
            List of project templates
        """
        return list()

    def get_example_urls(self) -> List[str]:
        """
        Returns a list of URLs that a series of Examples for plugin can be downloaded from.

        Returns:
            List of urls
        """
        return list()

    def get_help_urls(self) -> Dict[str, str]:
        """
        Returns a dictionary of topics and links to help.

        Returns:
            Dict of help urls
        """
        return dict()

    @staticmethod
    def get_version_url(version: str, extra: str = None,
                        repo_base_url: str = 'https://github.com/InstituteforDiseaseModeling/idmtools/tree/',
                        nightly_branch: str = 'dev'):
        """
        Build a url using version.

        Here we assume the tag will exist for that specific version
        Args:
            version: Version to look up. If it contains nightly, we default to nightly_branch
            extra: Extra parts of url pass base
            repo_base_url: Optional url
            nightly_branch: default to dev
        Returns:
            URL for item
        """
        return f'{repo_base_url}{nightly_branch if "nightly" in version else version[0:6]}/{extra}'

    def get_version(self) -> str:
        """
        Returns the version of the plugin.

        Returns:
            Version for the plugin
        """
        return None
