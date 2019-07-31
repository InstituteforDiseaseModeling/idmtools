from colorama import init

from idmtools.entities.IPlatformCli import PlatformCLIPlugins
from idmtools_platform_local.cli.base import cli


def main():
    init()
    platform_plugins = PlatformCLIPlugins()
    # Trigger the loading of additional cli from platforms
    [p.get_additional_commands() for p in platform_plugins.get_plugins()]
    cli()


# our entrypoint for our cli
if __name__ == '__main__':
    main()
