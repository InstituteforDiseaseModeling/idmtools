"""
idmtools process platform plugin definition.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from pathlib import Path
from typing import Type, Dict
from idmtools.entities.iplatform import IPlatform
from idmtools.registry.platform_specification import example_configuration_impl, get_platform_impl, \
    get_platform_type_impl, PlatformSpecification
from idmtools.registry.plugin_specification import get_description_impl
from idmtools_platform_container.container_platform import ContainerPlatform

CONTAINER_EXAMPLE_CONFIG = """
[Process]
job_directory = /data
"""


class ContainerPlatformSpecification(PlatformSpecification):
    """
    Process Platform Specification definition.
    """

    @get_description_impl
    def get_description(self) -> str:
        """
        Retrieve description.
        """
        return "Provides access to the Container Platform to IDM Tools"

    @get_platform_impl
    def get(self, **configuration) -> IPlatform:
        """
        Build our process platform from the passed in configuration object.

        We do our import of platform here to avoid any weirdness
        Args:
            configuration:
        Returns:
            IPlatform
        """
        return ContainerPlatform(**configuration)

    @example_configuration_impl
    def example_configuration(self):
        """
        Retrieve example configuration.
        """
        return CONTAINER_EXAMPLE_CONFIG

    @get_platform_type_impl
    def get_type(self) -> Type[ContainerPlatform]:  # noqa: F821
        """
        Get type.
        Returns:
            Type
        """
        return ContainerPlatform

    def get_version(self) -> str:
        """
        Returns the version of the plugin.
        Returns:
            Plugin Version
        """
        from idmtools_platform_container import __version__
        return __version__

    def get_configuration_aliases(self) -> Dict[str, Dict]:
        """
        Provides configuration aliases that exist in CONTAINER.
        """
        config_aliases = dict(
            CONTAINER=dict(
                job_directory=str(Path.home())
            )
        )
        return config_aliases
