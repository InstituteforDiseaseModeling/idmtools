"""Base click group definition."""
import logging
from idmtools import IdmConfigParser
from idmtools.core.logging import setup_logging, IdmToolsLoggingConfig
import click
from click_plugins import with_plugins
from pkg_resources import iter_entry_points
from idmtools_cli.iplatform_cli import IPlatformCLI

# Decorator for CLI functions that will require a platform object passed down to them
pass_platform_cli = click.make_pass_decorator(IPlatformCLI)


@with_plugins(iter_entry_points('idmtools_cli.cli_plugins'))
@click.group()
@click.option('--debug/--no-debug', default=False, help="When selected, enables console level logging")
def cli(debug):
    """Allows you to perform multiple idmtools commands."""
    IdmConfigParser()
    # init config by just calling config parser
    if debug:
        setup_logging(IdmToolsLoggingConfig(console=True, level=logging.DEBUG, force=True))
