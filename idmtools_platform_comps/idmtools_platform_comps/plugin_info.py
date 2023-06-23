"""idmtools comps platform plugin definition.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from logging import getLogger
from typing import Type, List, Dict
from idmtools.registry.platform_specification import example_configuration_impl, get_platform_impl, \
    get_platform_type_impl, PlatformSpecification
from idmtools.registry.plugin_specification import get_description_impl
from idmtools_platform_comps.comps_platform import COMPSPlatform
from idmtools_platform_comps.ssmt_platform import SSMTPlatform

COMPS_EXAMPLE_CONFIG = """
[COMPSPLATFORM]
endpoint = https://comps2.idmod.org
environment = Bayesian
priority = Lowest
simulation_root = $COMPS_PATH(USER)\\output
node_group = emod_abcd
num_retries = 0
num_cores = 1
max_workers = 16
batch_size = 10
min_time_between_commissions = 20
exclusive = False
# Optional config option. It is recommended you only use this in advanced scenarios. Otherwise
# leave it unset
docker_image = docker-staging.packages.idmod.org/idmtools/comps_ssmt_worker:1.0.0
"""

logger = getLogger(__name__)


class COMPSPlatformSpecification(PlatformSpecification):
    """Provide the plugin definition for COMPSPlatform."""

    def __init__(self):
        """Constructor."""
        logger.debug("Initializing COMPS Specification")

    @get_description_impl
    def get_description(self) -> str:
        """Get description."""
        return "Provides access to the COMPS Platform to idmtools"

    @get_platform_impl
    def get(self, **configuration) -> COMPSPlatform:
        """Get COMPSPlatform object with configuration."""
        return COMPSPlatform(**configuration)

    @example_configuration_impl
    def example_configuration(self):
        """Get example config."""
        return COMPS_EXAMPLE_CONFIG

    @get_platform_type_impl
    def get_type(self) -> Type[COMPSPlatform]:
        """Get COMPSPlatform type."""
        return COMPSPlatform

    def get_example_urls(self) -> List[str]:
        """Get Comps examples."""
        from idmtools_platform_comps import __version__
        examples = [f'examples/{example}' for example in ['ssmt', 'workitem', 'vistools']]
        return [self.get_version_url(f'v{__version__}', x) for x in examples]

    def get_version(self) -> str:
        """
        Returns the version of the plugin.

        Returns:
            Plugin Version
        """
        from idmtools_platform_comps import __version__
        return __version__

    def get_configuration_aliases(self) -> Dict[str, Dict]:
        """Provides configuration aliases that exist in COMPS."""
        config_aliases = dict(
            BELEGOST=dict(
                endpoint="https://comps.idmod.org",
                environment="Belegost"
            ),
            CALCULON=dict(
                endpoint="https://comps.idmod.org",
                environment="Calculon"
            ),
            IDMCLOUD=dict(
                endpoint="https://comps.idmod.org",
                environment="IDMcloud"
            ),
            NDCLOUD=dict(
                endpoint="https://comps.idmod.org",
                environment="NDcloud"
            ),
            BMGF_IPMCLOUD=dict(
                endpoint="https://comps.idmod.org",
                environment="BMGF_IPMcloud"
            ),
            QSTART=dict(
                endpoint="https://comps.idmod.org",
                environment="Qstart"
            ),
            BAYESIAN=dict(
                endpoint="https://comps2.idmod.org",
                environment="Bayesian"
            ),
            SLURMSTAGE=dict(
                endpoint="https://comps2.idmod.org",
                environment="SlurmStage"
            ),
            CUMULUS=dict(
                endpoint="https://comps2.idmod.org",
                environment="Cumulus"
            )
        )
        config_aliases['SLURM'] = config_aliases['CALCULON']
        config_aliases['SLURM2'] = config_aliases['SLURMSTAGE']
        # Friendly names for dev/staging environments from @clorton
        config_aliases['BOXY'] = config_aliases['SLURMSTAGE']
        return config_aliases


class SSMTPlatformSpecification(COMPSPlatformSpecification):
    """Provides the plugic spec for SSMTPlatform."""

    def __init__(self):
        """Constructor."""
        logger.debug("Initializing SSMT Specification")

    @get_description_impl
    def get_description(self) -> str:
        """Provide description of SSMT plugin."""
        return "Provides access to the SSMT Platform to idmtools"

    @get_platform_impl
    def get(self, **configuration) -> SSMTPlatform:
        """Get an instance of SSMTPlatform using the configuration."""
        return SSMTPlatform(**configuration)

    @example_configuration_impl
    def example_configuration(self):
        """Get example config."""
        # TODO determine different config and how we handle remotely
        return COMPS_EXAMPLE_CONFIG

    @get_platform_type_impl
    def get_type(self) -> Type[SSMTPlatform]:
        """Get SSMT type."""
        return SSMTPlatform

    def get_example_urls(self) -> List[str]:
        """Get SSMT example urls."""
        from idmtools_platform_comps import __version__
        examples = [f'examples/{example}' for example in ['ssmt', 'vistools']]
        return [self.get_version_url(f'v{__version__}', x) for x in examples]

    def get_version(self) -> str:
        """
        Returns the version of the plugin.

        Returns:
            Plugin Version
        """
        from idmtools_platform_comps import __version__
        return __version__

    def get_configuration_aliases(self) -> Dict[str, Dict]:
        """Provides configuration aliases that exist in COMPS."""
        config_aliases = super().get_configuration_aliases()
        ssmt_config_aliases = {f"{a}_SSMT": p for a, p in config_aliases.items()}
        return ssmt_config_aliases
