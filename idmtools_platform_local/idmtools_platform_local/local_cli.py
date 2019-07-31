from typing import NoReturn, Optional, List, Tuple

from idmtools.core.system_information import get_system_information
from idmtools.entities.IPlatformCli import PlatformCLISpecification, IPlatformCLI
from idmtools_cli.cli import experiment, simulation
from idmtools_platform_local.local_platform import LocalPlatform


class LocalCLI(IPlatformCLI):

    def get_experiment_status(self,  id: Optional[str], tags: Optional[List[Tuple[str, str]]]) -> NoReturn:
        experiment.status(id, tags)

    def get_simulation_status(self, id: Optional[str], experiment_id: Optional[str], status: Optional[str],
               tags: Optional[List[Tuple[str, str]]]) -> NoReturn:
        """

        Args:
            id:
            experiment_id:
            status:
            tags:

        Returns:

        """
        simulation.status(id, tags)

    def get_platform_information(self, platform: LocalPlatform) -> dict:
        local_info = get_system_information()
        worker_info = None
        running_containers = [dict(id=c.id, name=c.name, image=c.image) for c in platform.docker_manager.client.containers()]
        docker_info = dict(version=platform.docker_manager.client.version(),
                           data_usage=platform.docker_manager.client.df(),
                           full_info=platform.docker_manager.client.info(),
                           running_containers=running_containers
                           )


class LocalCLISpecification(PlatformCLISpecification):
    @staticmethod
    def get(configuration: dict) -> LocalCLI:
        return LocalCLI()

    @staticmethod
    def get_additional_commands() -> NoReturn:
        pass

    @staticmethod
    def get_description() -> str:
        return "Provides CLI commands for the Local Platform"
