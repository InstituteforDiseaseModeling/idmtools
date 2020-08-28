from logging import getLogger
from typing import Type, List
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
commission_batch_size = 50
min_time_between_commissions = 20
exclusive = False
# Optional config option. It is recommended you only use this in advanced scenarios. Otherwise
# leave it unset
docker_image = docker-staging.packages.idmod.org/idmtools/comps_ssmt_worker:1.0.0
"""

logger = getLogger(__name__)


class COMPSPlatformSpecification(PlatformSpecification):

    def __init__(self):
        logger.debug("Initializing COMPS Specification")

    @get_description_impl
    def get_description(self) -> str:
        return "Provides access to the COMPS Platform to idmtools"

    @get_platform_impl
    def get(self, **configuration) -> COMPSPlatform:
        return COMPSPlatform(**configuration)

    @example_configuration_impl
    def example_configuration(self):
        return COMPS_EXAMPLE_CONFIG

    @get_platform_type_impl
    def get_type(self) -> Type[COMPSPlatform]:
        return COMPSPlatform

    def get_example_urls(self) -> List[str]:
        from idmtools_platform_comps import __version__
        examples = [f'examples/{example}' for example in ['ssmt', 'workitem', 'vistools']]
        return [self.get_version_url(f'v{__version__}', x) for x in examples]


class SSMTPlatformSpecification(PlatformSpecification):

    def __init__(self):
        logger.debug("Initializing SSMT Specification")

    @get_description_impl
    def get_description(self) -> str:
        return "Provides access to the COMPS Platform to idmtools"

    @get_platform_impl
    def get(self, **configuration) -> COMPSPlatform:
        return SSMTPlatform(**configuration)

    @example_configuration_impl
    def example_configuration(self):
        # TODO determine different config and how we handle remotely
        return COMPS_EXAMPLE_CONFIG

    @get_platform_type_impl
    def get_type(self) -> Type[SSMTPlatform]:
        return SSMTPlatform

    def get_example_urls(self) -> List[str]:
        from idmtools_platform_comps import __version__
        examples = [f'examples/{example}' for example in ['ssmt', 'vistools']]
        return [self.get_version_url(f'v{__version__}', x) for x in examples]
