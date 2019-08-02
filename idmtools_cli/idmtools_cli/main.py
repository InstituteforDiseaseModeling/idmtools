from typing import NoReturn

from colorama import init
from idmtools_cli.cli import cli
from idmtools.entities.IPlatformCli import PlatformCLIPlugins


def main() -> NoReturn:
    """
    This is our main run function for the CLI. It basically calls start(load cli including the plugins) and then
    run the cli

    Returns:
        None
    """
    start()
    cli()


def start() -> NoReturn:
    """
    Loads the different components of the CLI

    Currently this involves

    1) Initializing colorama
    2) Loading built-in commands
    3) Loading Platform CLI items
    4) Loading custom CLI from platform plugins
    Returns:
        None
    """
    init()
    import idmtools_cli.cli.experiment
    import idmtools_cli.cli.simulation
    import idmtools_cli.cli.system_info  # noqa: F401
    platform_plugins = PlatformCLIPlugins()
    # Trigger the loading of additional cli from platforms
    [p.get_additional_commands() for p in platform_plugins.get_plugins()]


# our entrypoint for our cli
if __name__ == '__main__':
    main()
