from typing import NoReturn, Optional, List, Tuple
from idmtools.entities.IPlatformCli import PlatformCLISpecification, IPlatformCLI


class LocalCLI(IPlatformCLI):

    def get_experiment_status(self, id: Optional[str], tags: Optional[List[Tuple[str, str]]]) -> NoReturn:
        from idmtools_cli.cli import experiment
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
        from idmtools_cli.cli import simulation
        simulation.status(id, tags)

    def get_platform_information(self, platform: 'LocalPlatform') -> dict:  # noqa: F821
        pass
        # local_info = get_system_information()
        # worker_info = None
        # running_containers = [dict(id=c.id, name=c.name, image=c.image) for c in
        #                      platform.docker_manager.client.containers()]
        # docker_info = dict(version=platform.docker_manager.client.version(),
        #                   data_usage=platform.docker_manager.client.df(),
        #                   full_info=platform.docker_manager.client.info(),
        #                   running_containers=running_containers
        #                   )


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
