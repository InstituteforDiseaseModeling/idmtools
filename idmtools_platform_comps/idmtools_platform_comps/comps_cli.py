from typing import NoReturn
from idmtools.entities.IPlatformCli import PlatformCLISpecification, IPlatformCLI


class CompsCLI(IPlatformCLI):

    def get_experiment_status(self, *args, **kwargs) -> NoReturn:
        pass

    def get_simulation_status(self, *args, **kwargs) -> NoReturn:
        pass

    def get_platform_information(self) -> dict:
        pass


class CompsCLISpecification(PlatformCLISpecification):
    @staticmethod
    def get(configuration: dict) -> CompsCLI:
        pass

    @staticmethod
    def get_additional_commands() -> NoReturn:
        pass

    @staticmethod
    def get_description() -> str:
        return "Provides CLI commands for the COMPS Platform"
