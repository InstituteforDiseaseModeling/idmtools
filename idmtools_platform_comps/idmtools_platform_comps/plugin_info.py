from logging import getLogger
from typing import Type

from idmtools.entities import IPlatform
from idmtools.registry.platform_specification import example_configuration_impl, get_platform_impl, \
    get_platform_type_impl, PlatformSpecification
from idmtools.registry.plugin_specification import get_description_impl
from idmtools_platform_comps.comps_platform import COMPSPlatform

COMPS_EXAMPLE_CONFIG = """
[COMPSPLATFORM]
endpoint = https://comps2.idmod.org
environment = Bayesian
priority = Lowest
simulation_root = $COMPS_PATH(USER)\\output
node_group = emod_abcd
num_retires = 0
num_cores = 1
exclusive = False
"""

logger = getLogger(__name__)


class COMPSPlatformSpecification(PlatformSpecification):

    def __init__(self):
        logger.debug("Initializing COMPS Specification")

    @get_description_impl
    def get_description(self) -> str:
        return "Provides access to the COMPS Platform to IDM-Tools"

    @get_platform_impl
    def get(self, configuration: dict) -> IPlatform:
        return COMPSPlatform(**configuration)

    @example_configuration_impl
    def example_configuration(self):
        return COMPS_EXAMPLE_CONFIG

    @get_platform_type_impl
    def get_type(self) -> Type[COMPSPlatform]:
        return COMPSPlatform
