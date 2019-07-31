from tabulate import tabulate

from idmtools.core.system_information import get_system_information
from idmtools.entities.IPlatform import PlatformPlugins
from idmtools_cli.cli.base import cli
from idmtools_cli.cli.experiment import supported_platforms


@cli.group(help="Troubleshooting or debugging information")
def info():
    pass


@info.command()
def system_information():
    system_info = get_system_information()
    print(tabulate(system_info.to_dict()))


@info.group(help="Commands to get information about installed idmtools plugins")
def plugins():
    pass


@plugins.command()
def cli_plugins():
    print(tabulate(supported_platforms.keys()))


@plugins.command()
def platform_plugins():
    platforms = PlatformPlugins().get_plugin_map().keys()
    print(tabulate(platforms))
