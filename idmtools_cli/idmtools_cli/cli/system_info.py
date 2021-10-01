"""
Defines the info group cli command and version command as well.
"""
from collections import defaultdict

import os
from logging import getLogger, DEBUG
import stat
import click
import pyperclip

from idmtools.registry.master_plugin_registry import MasterPluginRegistry
from idmtools.registry.task_specification import TaskPlugins
from tabulate import tabulate
from idmtools.core.system_information import get_system_information
from idmtools.registry.platform_specification import PlatformPlugins
from idmtools_cli.cli.entrypoint import cli
from idmtools_cli.cli.experiment import supported_platforms
from idmtools_cli.utils.cols import columns

logger = getLogger(__name__)


@cli.command(help="List version info about idmtools and plugins")
@click.option('--no-plugins/--plugins', default=False, help="Control whether we display plugins with modules")
def version(no_plugins: bool):
    """Returns version of all idmtools components."""
    from idmtools import __version__
    from idmtools_cli import __version__ as cli_version
    plugin_map = MasterPluginRegistry().get_plugin_map()
    module_map = defaultdict(dict)
    for name in sorted(plugin_map.keys()):
        try:
            spec = plugin_map[name]
            module_name = str(spec.get_type().__module__)
            if module_name:
                module_name = module_name.split(".")[0]
        except Exception as e:
            if logger.isEnabledFor(DEBUG):
                logger.exception(e)
            module_name = 'Unknown Module'
        if plugin_map[name].get_version():
            module_map[module_name][name] = plugin_map[name].get_version()

    if not module_map['idmtools']:
        module_map['idmtools'] = __version__

    if not module_map['idmtools-cli']:
        module_map['idmtools-cli'] = cli_version

    for module in sorted(module_map.keys()):
        if isinstance(module_map[module], dict):
            mod_version = list(module_map[module].values())[0]
            click.echo(click.style(columns((module.replace("_", "-"), 36), (f'Version: {mod_version}', 40)), fg='green'))
            if not no_plugins:
                click.echo(click.style('  Plugins:', fg='yellow'))
                for plugin_name in sorted(module_map[module].keys()):
                    click.echo(click.style(columns(('', 3), (f'{plugin_name}', 25)), fg='blue'))
        else:
            click.echo(click.style(columns((module.replace("_", "-"), 36), (f'Version: {module_map[module]}', 40)), fg='green'))


@cli.group(help="Troubleshooting and debugging information")
def info():
    """Info cli subcommand."""
    pass


@info.command(help="Provide an output with details about your current execution platform and IDM-Tools install")
@click.option('--copy-to-clipboard/--no-copy-to-clipboard', default=False, help="Copy output to clipboard")
@click.option('--no-format-for-gh/--format-for-gh', default=False, help="When copying to clipboard, do we want to "
                                                                        "formatted for Github")
@click.option('--issue/--no-issue', default=False, help="Copy data and format for github alias")
@click.option('--output-filename', default=None, help="Output filename")
def system(copy_to_clipboard, no_format_for_gh, issue, output_filename):
    """Provide info about your current install of idmtools."""
    logger.debug("Building system info")
    system_info = get_system_information()
    logger.debug("Building system info output")
    lines = [f'System Information\n{"=" * 20}']
    ordered_fields = sorted(system_info.__dict__.keys())
    [lines.append(f'{k}: {system_info.__dict__[k]}') for k in ordered_fields]
    if os.name != 'nt':
        logger.debug("Building windows info")
        for f in ['workers', 'redis-data']:
            fname = os.path.join(system_info.data_directory, f)
            if os.path.exists(fname):
                from pwd import getpwuid
                s = os.stat(fname)
                owned_by = f'{getpwuid(s.st_uid).pw_name} UID {s.st_uid}:{s.st_gid}'
                lines.append(f'{fname} has permissions of {oct(stat.S_IMODE(os.lstat(fname).st_mode))} '
                             f'and is owned by {owned_by}')
        logger.debug("Windows info done")
    try:
        import docker
        logger.debug("Building docker info")
        lines.append(f'\nDocker Information\n{"=" * 20}')
        client = docker.from_env()
        lines.append(f'Version: {client.version()}')
        docker_info = client.info()
        ordered_fields = sorted(docker_info.keys())
        [lines.append(f'{k}: {docker_info[k]}') for k in ordered_fields]
        logger.debug("docker info done")
    except ImportError:
        pass
    except Exception as e:
        logger.error(e)
        raise e
    if copy_to_clipboard:
        logger.debug("Copying to clipboard")
        output = '\n'.join(lines)
        if not no_format_for_gh or issue:
            logger.debug('Formatting for github')
            # let's remove system information here by rebuilding without it
            output = '\n'.join(lines[0:])
            output = f'```### System Information\n{output}````'
        pyperclip.copy(output)
    if output_filename is not None:
        with open(output_filename, 'w') as log_out:
            log_out.writelines(lines)
    else:
        logger.debug("Writing output")
        for line in lines:
            click.echo(line)


@info.group(help="Commands to get information about installed IDM-Tools plugins")
def plugins():
    """Info about plugins installed."""
    pass


@plugins.command(help="List CLI plugins")
def cli():
    """List CLI plugins."""
    items = list(supported_platforms.keys())
    print(tabulate([[x] for x in items], headers=['CLI Plugins'], tablefmt='psql'))


@plugins.command(help="List Platform plugins configuration aliases")
def platform_aliases():
    """List platform aliases."""
    aliases = PlatformPlugins().get_aliases()
    print(tabulate([[name, details[1]] for name, details in aliases.items()], headers=['Platform Plugin Aliases', "Configuration Options"], tablefmt='psql'))


@plugins.command(help="List Platform plugins")
def platform():
    """List platform plugins."""
    platforms = PlatformPlugins().get_plugin_map().keys()
    print(tabulate([[x] for x in platforms], headers=['Platform Plugins'], tablefmt='psql'))


@plugins.command(help="List Task plugins")
def task():
    """List task plugins."""
    tasks = TaskPlugins().get_plugin_map().keys()
    print(tabulate([[x] for x in tasks], headers=['Task Plugins'], tablefmt='psql'))
