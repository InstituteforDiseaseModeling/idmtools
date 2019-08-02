from typing import Optional, Tuple, List
import click

from idmtools.entities.IPlatformCli import PlatformCLIPlugins, IPlatformCLI
from idmtools_cli.cli import cli, pass_platform_cli
from idmtools_cli.cli.utils import tags_help


supported_platforms = PlatformCLIPlugins().get_plugin_map()
# Decorator for CLI functions that will require a platform object passed down to them


@cli.group(help="Commands related to experiments(top-level jobs)")
@click.option('--platform', type=click.Choice(supported_platforms.keys()))
@click.option('--config-name', default=None, type=str, help='Name of platform section in our idmtools.ini to use as '
                                                            'configuration')
@click.pass_context
def experiment(ctx, platform, config_name):
    """
    Contains commands related to experiments
    """
    config = dict() if config_name is None else config_name
    # create our platform object and pass it along through the context to any sub-commands
    ctx.obj = supported_platforms[platform].get(config)


@experiment.command()
@pass_platform_cli
@click.option('--id', default=None, help="Filter status by experiment ID")
@click.option('--tags', default=None, nargs=2, multiple=True, help=tags_help)
def status(platform_cli: IPlatformCLI, id: Optional[str], tags: Optional[List[Tuple[str, str]]]):
    """
    List the status of experiment(s) with the ability to filter by experiment id and tags
    """
    platform_cli.get_experiment_status(id, tags)
