from typing import NoReturn, Optional, List, Tuple
from idmtools.registry.PluginSpecification import get_description_impl
from idmtools_cli.IPlatformCli import IPlatformCLI, PlatformCLISpecification, get_platform_cli_impl, \
    get_additional_commands_impl
from idmtools_platform_local.cli import experiment, simulation


class LocalCLI(IPlatformCLI):

    def get_experiment_status(self, id: Optional[str], tags: Optional[List[Tuple[str, str]]]) -> NoReturn:
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

        simulation.status(id, experiment_id, status, tags)

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
    @get_platform_cli_impl
    def get(self, configuration: dict) -> LocalCLI:
        return LocalCLI()

    @get_additional_commands_impl
    def get_additional_commands(self) -> NoReturn:
        pass

    @get_description_impl
    def get_description(self) -> str:
        return "Provides CLI commands for the Local Platform"
