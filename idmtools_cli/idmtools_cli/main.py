"""Entrypoint for idmtools cli."""
import os
from typing import NoReturn
from colorama import init as color_init


def main() -> NoReturn:
    """
    This is our main run function for the CLI.

    It basically calls start(load cli including the plugins) and then run the cli.

    Returns:
        None
    """
    os.environ['IDMTOOLS_NO_CONFIG_WARNING'] = '1'
    from idmtools_cli.cli.entrypoint import cli
    start()
    cli(auto_envvar_prefix='IDMTOOLS_CLI')


def start() -> NoReturn:
    """
    Loads the different components of the CLI.

    Currently this involves

    1) Initializing colorama
    2) Loading built-in commands
    3) Loading Platform CLI items
    4) Loading custom CLI from platform plugins

    Returns:
        None
    """
    from idmtools_cli.iplatform_cli import PlatformCLIPlugins
    color_init()
    import idmtools_cli.cli.init  # noqa: F401
    import idmtools_cli.cli.config_file  # noqa: F401
    import idmtools_cli.cli.system_info  # noqa: F401
    import idmtools_cli.cli.gitrepo  # noqa: F401
    import idmtools_cli.cli.package  # noqa: F401
    platform_plugins = PlatformCLIPlugins()
    from idmtools_cli.cli.init import build_project_commands
    build_project_commands()
    # Trigger the loading of additional cli from platforms
    [p.get_additional_commands() for p in platform_plugins.get_plugins()]


# our entrypoint for our cli
if __name__ == '__main__':
    main()
