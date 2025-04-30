"""
idmtools slurm platform plugin definition.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from pathlib import Path
from typing import Type, Dict

from idmtools.entities.iplatform import IPlatform
from idmtools.registry.platform_specification import example_configuration_impl, get_platform_impl, \
    get_platform_type_impl, PlatformSpecification
from idmtools.registry.plugin_specification import get_description_impl


SLURM_EXAMPLE_CONFIG = """
[Slurm]
# mode of operation. Options are ssh or local
# SSH would mean you remotely connect to the head node to submit jobs to slurm(and use that to transfer files as well)
# Local is when you install idmtools on the head node and run from there
mode = ssh
job_directory = /data
# values on ALL or END. 
# All will email you as the job changes states
# END with email you when the job is done
mail_type = 'END'
mail_user = 'ccollins@idmod.org'
"""


class SlurmPlatformSpecification(PlatformSpecification):

    @get_description_impl
    def get_description(self) -> str:
        return "Provides access to the Local Platform to IDM Tools"

    @get_platform_impl
    def get(self, **configuration) -> IPlatform:
        """
        Build our slurm platform from the passed in configuration object

        We do our import of platform here to avoid any weirdness
        Args:
            configuration:

        Returns:

        """
        from idmtools_platform_slurm.slurm_platform import SlurmPlatform
        return SlurmPlatform(**configuration)

    @example_configuration_impl
    def example_configuration(self):
        return SLURM_EXAMPLE_CONFIG

    @get_platform_type_impl
    def get_type(self) -> Type['SlurmPlatform']:  # noqa: F821
        from idmtools_platform_slurm.slurm_platform import SlurmPlatform
        return SlurmPlatform

    def get_version(self) -> str:
        """
        Returns the version of the plugin

        Returns:
            Plugin Version
        """
        from idmtools_platform_slurm import __version__
        return __version__

    def get_configuration_aliases(self) -> Dict[str, Dict]:
        """Provides configuration aliases that exist in SLURM."""
        config_aliases = dict(
            SLURM_LOCAL=dict(
                job_directory=str(Path.home())
            )
        )
        return config_aliases
