"""idmtools local platform cli interface.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from typing import NoReturn, Optional, List, Tuple
from idmtools.registry.plugin_specification import get_description_impl
from idmtools_cli.iplatform_cli import IPlatformCLI, PlatformCLISpecification, get_platform_cli_impl, \
    get_additional_commands_impl
from idmtools_platform_local.cli import experiment, simulation


class LocalCLI(IPlatformCLI):
    """Provides the LocalCLI implementation of the common PlatformCLI interface."""

    def get_experiment_status(self, id: Optional[str], tags: Optional[List[Tuple[str, str]]]) -> NoReturn:
        """Get experiment status."""
        experiment.status(id, tags)

    def get_simulation_status(self, id: Optional[str], experiment_id: Optional[str], status: Optional[str],
                              tags: Optional[List[Tuple[str, str]]]) -> NoReturn:
        """
        Get simulation status.
        """
        simulation.status(id, experiment_id, status, tags)

    def get_platform_information(self, platform: 'LocalPlatform') -> dict:  # noqa: F821
        """Get simulation information."""
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
    """Provides plugin spec for LocalCLI."""
    @get_platform_cli_impl
    def get(self, configuration: dict) -> LocalCLI:
        """Get CLI using provided configuration."""
        return LocalCLI()

    @get_additional_commands_impl
    def get_additional_commands(self) -> NoReturn:
        """Load our cli commands."""
        from idmtools_platform_local.cli.experiment import extra_commands
        extra_commands()

    @get_description_impl
    def get_description(self) -> str:
        """Get description of our cli plugin."""
        return "Provides CLI commands for the Local Platform"
