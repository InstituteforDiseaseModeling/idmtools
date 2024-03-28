"""Base click group definition."""
import logging
from idmtools import IdmConfigParser
from idmtools.core.logging import setup_logging, IdmToolsLoggingConfig
import click
from click_plugins import with_plugins

try:
    from importlib.metadata import entry_points
except ImportError:
    from importlib_metadata import entry_points  # for python 3.7
from idmtools_cli.iplatform_cli import IPlatformCLI

# Decorator for CLI functions that will require a platform object passed down to them
pass_platform_cli = click.make_pass_decorator(IPlatformCLI)


def get_filtered_entry_points(group):
    """
    Get entry points for a specific group, compatible across Python versions.

    Args:
        group (str): The entry point group to filter by.

    Returns:
        An iterable of entry point objects for the specified group.
    """
    # For Python 3.10 and newer, use the select method if available
    if hasattr(entry_points(), 'select'):
        return entry_points().select(group=group)
    else:
        # For Python 3.9 and earlier, manually filter the entry points
        return (ep for ep in entry_points().get(group, []))


@with_plugins(get_filtered_entry_points('idmtools_cli.cli_plugins'))
@click.group()
@click.option('--debug/--no-debug', default=False, help="When selected, enables console level logging")
def cli(debug):
    """Allows you to perform multiple idmtools commands."""
    IdmConfigParser()
    # init config by just calling config parser
    if debug:
        setup_logging(IdmToolsLoggingConfig(console=True, level=logging.DEBUG, force=True))
