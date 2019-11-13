import os
from logging import getLogger
import stat
import click
import pyperclip
from tabulate import tabulate

from idmtools.core.system_information import get_system_information
from idmtools.registry.platform_specification import PlatformPlugins
from idmtools_cli.cli import cli
from idmtools_cli.cli.experiment import supported_platforms

logger = getLogger(__name__)


@cli.group(help="Troubleshooting and debugging information")
def info():
    pass


@info.command(help="Provide an output with details about your current execution platform and IDM-Tools install")
@click.option('--copy-to-clipboard/--no-copy-to-clipboard', default=False, help="Copy output to clipboard")
@click.option('--no-format-for-gh/--format-for-gh', default=False, help="When copying to clipboard, do we want to "
                                                                        "formatted for Github")
@click.option('--issue/--no-issue', default=False, help="Copy data and format for github alias")
def system(copy_to_clipboard, no_format_for_gh, issue):
    system_info = get_system_information()
    lines = [f'System Information\n{ "=" * 20}']
    ordered_fields = sorted(system_info.__dict__.keys())
    [lines.append(f'{k}: {system_info.__dict__[k]}') for k in ordered_fields]
    if os.name != 'nt':
        for f in ['workers', 'redis-data']:
            fname = os.path.join(system_info.data_directory, f)
            if os.path.exists(fname):
                lines.append(f'{fname} has permissions of {oct(stat.S_IMODE(os.lstat(fname).st_mode))}')
    try:
        import docker
        lines.append(f'\nDocker Information\n{ "=" * 20}')
        client = docker.from_env()
        lines.append(f'Version: {client.version()}')
        docker_info = client.info()
        ordered_fields = sorted(docker_info.keys())
        [lines.append(f'{k}: {docker_info[k]}') for k in ordered_fields]
    except ImportError:
        pass
    if copy_to_clipboard:
        output = '\n'.join(lines)
        if not no_format_for_gh or issue:
            logger.debug('Formatting for githubb')
            # let's remove system information here by rebuilding without it
            output = '\n'.join(lines[0:])
            output = f'```### System Information\n{output}````'
        pyperclip.copy(output)

    for line in lines:
        click.echo(line)


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
