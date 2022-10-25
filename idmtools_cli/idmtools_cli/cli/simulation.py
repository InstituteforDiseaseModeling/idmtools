"""
Defines the CLI simulation command group.
"""
from typing import Optional, Tuple, List
import click
from idmtools_cli.iplatform_cli import IPlatformCLI
from idmtools_cli.cli.entrypoint import pass_platform_cli, cli
from idmtools_cli.cli.utils import tags_help, get_platform_from_config_or_name, supported_platforms


@cli.group()
@click.option('--platform', default=None, type=click.Choice(supported_platforms.keys()))
@click.option('--config-block', default=None, type=str, help='Name of platform section in our idmtools.ini to use as '
                                                             'configuration')
@click.pass_context
def simulation(ctx, platform, config_block):
    """
    Contains commands related to simulations.

    Some useful examples are

    Get the status of simulations for the platform using the local platform defaults, you would run
    idmtools simulation --platform Local status --help
    """
    platform_obj = get_platform_from_config_or_name(config_block, platform)
    # create our platform object and pass it along through the context to any sub-commands
    ctx.obj = platform_obj


@simulation.command()
@pass_platform_cli
@click.option('--id', default=None, help="Filter status by simulation ID")
@click.option('--experiment-id', default=None, help="Filter status by experiment ID")
# @click.option('--status', default=None, type=click.Choice([e.value for e in Status]))
@click.option('--tags', default=None, nargs=2, multiple=True, help=tags_help)
def status(platform_cli: IPlatformCLI, id: Optional[str], experiment_id: Optional[str],
           tags: Optional[List[Tuple[str, str]]]):
    """
    List of statuses for simulation(s) with the ability to filter by id, experiment_id, status, and tags.

    For Example
    Get the status of simulations for the platform using the local platform defaults, you would run
    idmtools simulation --platform Local status

    Another example would be to use a platform defined in a configuration block while also filtering tags where a == 0
    idmtools simulation --config-block COMPS2 status --tags a 0

    Multiple tags
    idmtools simulation --config-block COMPS2 status --tags a 0 --tags a 3
    """
    platform_cli.get_simulation_status(id, experiment_id, None, tags)
