from idmtools.entities.iplatform import IPlatform
from typing import Type
from idmtools.registry.experiment_specification import example_configuration_impl
from idmtools.registry.platform_specification import PlatformSpecification, get_platform_impl, get_platform_type_impl
from idmtools.registry.plugin_specification import get_description_impl

FILE_PLATFORM_EXAMPLE_CONFIG = """
"""


class FilePlatformSpecification(PlatformSpecification):
    @get_description_impl
    def get_description(self) -> str:
        return "Provides access to the Local Platform to IDM Tools"

    @get_platform_impl
    def get(self, **configuration) -> IPlatform:
        """
        Build our file platform from the passed in configuration object

        We do our import of platform here to avoid any weird issues on plugin load

        Args:
            configuration:

        Returns:

        """
        from idmtools_platform_file.file_platform import FilePlatform
        return FilePlatform(**configuration)

    @example_configuration_impl
    def example_configuration(self):
        return FILE_PLATFORM_EXAMPLE_CONFIG

    @get_platform_type_impl
    def get_type(self) -> Type['FilePlatform']:  # noqa: F821
        from idmtools_platform_file.file_platform import FilePlatform
        return FilePlatform

    def get_version(self) -> str:
        """
        Returns the version of the plugin

        Returns:
            Plugin Version
        """
        from idmtools_platform_file import __version__
        return __version__
