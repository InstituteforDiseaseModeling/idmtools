from logging import getLogger

import pluggy

PLUGIN_REFERENCE_NAME = 'idmtools_plugins'
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

    @get_description_spec
    def get_description(self) -> str:
        """
        A brief description of the plugin and its functionality

        Returns:

        """
        raise NotImplementedError("The plugin did not implement a description!")
