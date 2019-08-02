from typing import Optional, Tuple, List
import click

from idmtools.entities.IPlatformCli import PlatformCLIPlugins, IPlatformCLI
from idmtools_cli.cli import cli
from idmtools_cli.cli.experiment import pass_platform_cli
from idmtools_cli.cli.utils import tags_help


supported_platforms = PlatformCLIPlugins().get_plugin_map()


@cli.group(help="Commands related to simulations(sub-level jobs)")
@click.option('--platform', type=click.Choice(supported_platforms.keys()))
@click.option('--config-name', default=None, type=str, help='Name of platform section in our idmtools.ini to use as '
                                                            'configuration')
@click.pass_context
def simulation(ctx, platform, config_name):
    """
    Commands related to simulations
    """
    config = dict() if config_name is None else config_name
    # create our platform object and pass it along through the context to any sub-commands
    ctx.obj = supported_platforms[platform].get(config)


@simulation.command()
@pass_platform_cli
@click.option('--id', default=None, help="Filter status by simulation ID")
@click.option('--experiment-id', default=None, help="Filter status by experiment ID")
# @click.option('--status', default=None, type=click.Choice([e.value for e in Status]))
@click.option('--tags', default=None, nargs=2, multiple=True, help=tags_help)
def status(platform_cli: IPlatformCLI, id: Optional[str], experiment_id: Optional[str], status: Optional[str],
           tags: Optional[List[Tuple[str, str]]]):
    """
    List of statuses for simulation(s) with the ability to filter by id, experiment_id, status, and tags
    """
    platform_cli.get_simulation_status(id, experiment_id, status, tags)
