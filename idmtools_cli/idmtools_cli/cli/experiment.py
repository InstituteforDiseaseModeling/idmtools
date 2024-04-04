"""Defines cli group experiment."""
from typing import Optional, Tuple, List
import click
from idmtools_cli.iplatform_cli import IPlatformCLI
from idmtools_cli.cli.entrypoint import pass_platform_cli, cli
from idmtools_cli.cli.utils import tags_help, get_platform_from_config_or_name, supported_platforms


@cli.group()
@click.option('--platform', default=None, type=click.Choice(supported_platforms.keys()),
              help='Currently only support Local Platform')
@click.option('--config-block', default=None, type=str, help='Name of platform section in our idmtools.ini to use as '
                                                             'configuration')
@click.pass_context
def experiment(ctx, platform, config_block):
    """
    Contains commands related to experiments for Local Platform.

    Some useful examples are

    Get the status of experiments for the platform defined by the "Local" configuration block

    Get the usage details of the status command:

    idmtools experiment --platform Local status --help

    """
    platform_obj = get_platform_from_config_or_name(config_block, platform)
    # create our platform object and pass it along through the context to any sub-commands
    ctx.obj = platform_obj


@experiment.command()
@pass_platform_cli
@click.option('--id', default=None, help="Filter status by experiment ID")
@click.option('--tags', default=None, nargs=2, multiple=True, help=tags_help)
def status(platform_cli: IPlatformCLI, id: Optional[str], tags: Optional[List[Tuple[str, str]]]):
    """
    List the status of experiment(s) with the ability to filter by experiment id and tags.

    Some examples:
    Get the status of simulations for the platform using the local platform defaults, you would run
    idmtools simulation --platform Local status

    Another example would be to use a platform defined in a configuration block while also filtering tags where a == 0
    idmtools experiment --config-block Local status --tags a 0

    Multiple tags:
    idmtools experiment --config-block Local status --tags a 0 --tags a 3
    """
    platform_cli.get_experiment_status(id, tags)
