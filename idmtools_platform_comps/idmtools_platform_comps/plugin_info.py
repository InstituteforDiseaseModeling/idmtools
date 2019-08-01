from idmtools.core.plugin_manager import get_description_impl
from idmtools.entities import IPlatform
from idmtools.entities.IPlatform import PlatformSpecification, example_configuration_impl, get_platform_impl
from idmtools_platform_comps.COMPSPlatform import COMPSPlatform

COMPS_EXAMPLE_CONFIG = """
[COMPSPLATFORM]
endpoint = https://comps2.idmod.org
environment = Bayesian
priority = Lowest
simulation_root = $COMPS_PATH(USER)\output
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
        return COMPSPlatform()

    @staticmethod
    @example_configuration_impl
    def example_configuration():
        return COMPS_EXAMPLE_CONFIG
