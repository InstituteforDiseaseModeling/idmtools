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

PROCESS_EXAMPLE_CONFIG = """
[Process]
job_directory = /data
"""


class ProcessPlatformSpecification(PlatformSpecification):
    """
    Process Platform Specification definition.
    """

    @get_description_impl
    def get_description(self) -> str:
        """
        Retrieve description.
        """
        return "Provides access to the Process Platform to IDM Tools"

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
        from process_platform import ProcessPlatform
        return ProcessPlatform(**configuration)

    @example_configuration_impl
    def example_configuration(self):
        """
        Retrieve example configuration.
        """
        return PROCESS_EXAMPLE_CONFIG

    @get_platform_type_impl
    def get_type(self) -> Type['ProcessPlatform']:  # noqa: F821
        """
        Get type.
        Returns:
            Type
        """
        from idmtools_platform_process.process_platform import ProcessPlatform
        return ProcessPlatform

    def get_version(self) -> str:
        """
        Returns the version of the plugin.
        Returns:
            Plugin Version
        """
        from idmtools_platform_process import __version__
        return __version__

    def get_configuration_aliases(self) -> Dict[str, Dict]:
        """
        Provides configuration aliases that exist in PROCESS.
        """
        config_aliases = dict(
            PROCESS=dict(
                job_directory=str(Path.home())
            )
        )
        return config_aliases
