from typing import Type

from idmtools.registry.PlatformSpecification import PlatformSpecification, get_platform_impl, \
    example_configuration_impl, get_platform_type_impl
from idmtools.registry.PluginSpecification import get_description_impl


from idmtools.entities import IPlatform


LOCAL_PLATFORM_EXAMPLE_CONFIG = """
[LOCAL]
redis_image=redis:5.0.4-alpine
redis_port=6379
runtime=nvidia
workers_image: str = 'idm-docker-production.packages.idmod.org:latest'
workers_ui_port: int = 5000
"""


class LocalPlatformSpecification(PlatformSpecification):

    @staticmethod
    @get_description_impl
    def get_description() -> str:
        return "Provides access to the Local Platform to IDM Tools"

    @staticmethod
    @get_platform_impl
    def get(configuration: dict) -> IPlatform:
        """
        Build our local platform from the passed in configuration object

        We do our import of platform here to avoid any weir
        Args:
            configuration:

        Returns:

        """
        from idmtools_platform_local.local_platform import LocalPlatform
        return LocalPlatform()

    @staticmethod
    @example_configuration_impl
    def example_configuration():
        return LOCAL_PLATFORM_EXAMPLE_CONFIG

    @staticmethod
    @get_platform_type_impl
    def get_type() -> Type['LocalPlatform']:
        from idmtools_platform_local.local_platform import LocalPlatform
        return LocalPlatform
