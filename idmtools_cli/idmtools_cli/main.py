from colorama import init
from idmtools_cli.cli.base import cli
from idmtools.entities.IPlatformCli import PlatformCLIPlugins


def main():
    start()
    cli()


def start():
    init()
    import idmtools_cli.cli.experiment
    import idmtools_cli.cli.simulation
    import idmtools_cli.cli.system_info
    platform_plugins = PlatformCLIPlugins()
    # Trigger the loading of additional cli from platforms
    [p.get_additional_commands() for p in platform_plugins.get_plugins()]


# our entrypoint for our cli
if __name__ == '__main__':
    main()
