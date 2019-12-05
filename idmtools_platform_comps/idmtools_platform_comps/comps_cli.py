from typing import NoReturn

from idmtools.registry.plugin_specification import get_description_impl
from idmtools_cli.iplatform_cli import IPlatformCLI, PlatformCLISpecification, get_platform_cli_impl, \
    get_additional_commands_impl


class CompsCLI(IPlatformCLI):

    def get_experiment_status(self, *args, **kwargs) -> NoReturn:
        pass

    def get_simulation_status(self, *args, **kwargs) -> NoReturn:
        pass

    def get_platform_information(self) -> dict:
        pass


class COMPSCLISpecification(PlatformCLISpecification):

    @get_platform_cli_impl
    def get(self, configuration: dict) -> CompsCLI:
        return CompsCLI(**configuration)

    @get_additional_commands_impl
    def get_additional_commands(self) -> NoReturn:
        import idmtools_platform_comps.cli.comps  # noqa: F401
        import idmtools_platform_comps.cli.utils  # noqa: F401

    @get_description_impl
    def get_description(self) -> str:
        return "Provides CLI commands for the COMPS Platform"
