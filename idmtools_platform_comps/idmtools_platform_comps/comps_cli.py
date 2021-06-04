"""Define the comps cli spec.

Notes:
    - We eventually need to deprecate this

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
try:  # since cli is not required but we always try to load file, wrap in try except
    from typing import NoReturn

    from idmtools.registry.plugin_specification import get_description_impl
    from idmtools_cli.iplatform_cli import IPlatformCLI, PlatformCLISpecification, get_platform_cli_impl, \
        get_additional_commands_impl

    class CompsCLI(IPlatformCLI):
        """Defines our CLI interface for COMPS using IPlatformCLI."""

        def get_experiment_status(self, *args, **kwargs) -> NoReturn:
            """Experiment status command."""
            pass

        def get_simulation_status(self, *args, **kwargs) -> NoReturn:
            """Simulation status command."""
            pass

        def get_platform_information(self) -> dict:
            """Platofrm info."""
            pass

    class COMPSCLISpecification(PlatformCLISpecification):
        """Provides plugin definition for CompsCLI."""

        @get_platform_cli_impl
        def get(self, configuration: dict) -> CompsCLI:
            """Get our CLI plugin with config."""
            return CompsCLI(**configuration)

        @get_additional_commands_impl
        def get_additional_commands(self) -> NoReturn:
            """Get our CLI commands."""
            import idmtools_platform_comps.cli.comps  # noqa: F401

        @get_description_impl
        def get_description(self) -> str:
            """Get COMPS CLI plugin description."""
            return "Provides CLI commands for the COMPS Platform"
except ImportError:
    pass
