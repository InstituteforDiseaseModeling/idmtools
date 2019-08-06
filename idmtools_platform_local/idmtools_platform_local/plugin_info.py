from typing import Type

from idmtools.registry.PlatformSpecification import example_configuration_impl, get_platform_impl, \
    get_platform_type_impl, PlatformSpecification
from idmtools.registry.PluginSpecification import get_description_impl


from idmtools.entities import IPlatform


LOCAL_PLATFORM_EXAMPLE_CONFIG = """
[LOCAL]
redis_image=redis:5.0.4-alpine
redis_port=6379
runtime=nvidia
workers_image: str = 'idm-docker-staging.packages.idmod.org:latest'
workers_ui_port: int = 5000
"""


class LocalPlatformSpecification(PlatformSpecification):

    @get_description_impl
    def get_description(self) -> str:
        return "Provides access to the Local Platform to IDM Tools"

    @get_platform_impl
    def get(self, configuration: dict) -> IPlatform:
        """
        Build our local platform from the passed in configuration object

        We do our import of platform here to avoid any weir
        Args:
            configuration:

        Returns:

        """
        from idmtools_platform_local.local_platform import LocalPlatform
        return LocalPlatform()

    @example_configuration_impl
    def example_configuration(self):
        return LOCAL_PLATFORM_EXAMPLE_CONFIG

    @get_platform_type_impl
    def get_type(self) -> Type['LocalPlatform']:
        from idmtools_platform_local.local_platform import LocalPlatform
        return LocalPlatform
