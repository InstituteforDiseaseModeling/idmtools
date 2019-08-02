import click
from tabulate import tabulate

from idmtools.core.system_information import get_system_information
from idmtools.entities.IPlatform import PlatformPlugins
from idmtools_cli.cli import cli
from idmtools_cli.cli.experiment import supported_platforms


@cli.group(help="Troubleshooting and debugging information")
def info():
    pass


@info.command(help="Provide an output with details about your current execution platform and IDM-Tools install")
def system_information():
    system_info = get_system_information()
    click.echo('System Information:')
    print('System Informat')
    for k, v in system_info.__dict__.items():
        click.echo(f'{k}: {v}')


@info.group(help="Commands to get information about installed IDM-Tools plugins")
def plugins():
    pass


@plugins.command(help="List CLI plugins")
def cli():
    items = list(supported_platforms.keys())
    print(tabulate([[x] for x in items], headers=['CLI Plugins'], tablefmt='psql'))


@plugins.command(help="List Platform plugins")
def platform():
    platforms = PlatformPlugins().get_plugin_map().keys()
    print(tabulate([[x] for x in platforms], headers=['Platform Plugins'], tablefmt='psql'))
