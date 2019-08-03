from typing import Type

from idmtools.entities import IPlatform
from idmtools.registry.PlatformSpecification import PlatformSpecification, get_platform_impl, \
    example_configuration_impl, get_platform_type_impl
from idmtools.registry.PluginSpecification import get_description_impl
from idmtools_platform_comps.COMPSPlatform import COMPSPlatform

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


class COMPSSpecification(PlatformSpecification):

    @staticmethod
    @get_description_impl
    def get_description() -> str:
        return "Provides access to the COMPS Platform to IDM-Tools"

    @staticmethod
    @get_platform_impl
    def get(configuration: dict) -> IPlatform:
        return COMPSPlatform(**configuration)

    @staticmethod
    @example_configuration_impl
    def example_configuration():
        return COMPS_EXAMPLE_CONFIG

    @staticmethod
    @get_platform_type_impl
    def get_type() -> Type[COMPSPlatform]:
        return COMPSPlatform
