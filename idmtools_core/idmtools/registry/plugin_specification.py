from logging import getLogger

import pluggy

PLUGIN_REFERENCE_NAME = 'idmtools_plugins'
get_description_spec = pluggy.HookspecMarker(PLUGIN_REFERENCE_NAME)
get_description_impl = pluggy.HookimplMarker(PLUGIN_REFERENCE_NAME)
logger = getLogger(__name__)


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
