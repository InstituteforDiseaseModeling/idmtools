"""idmtools local platform group.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import time

import click
import docker
import stringcase as stringcase
from colorama import Fore

from idmtools_cli.cli.entrypoint import cli
from idmtools_platform_local.cli.utils import get_service_info
from idmtools_platform_local.infrastructure.docker_io import DockerIO
from idmtools_platform_local.infrastructure.service_manager import DockerServiceManager


class LocalCliContext:
    """Local CLI Context."""
    do: DockerIO = None
    sm: DockerServiceManager = None

    def __init__(self, config=None):
        """Constructor."""
        client = docker.from_env()
        if config is None:
            config = dict()
        self.do = DockerIO()
        self.sm = DockerServiceManager(client, **config)


cli_command_type = LocalCliContext
pass_do = click.make_pass_decorator(LocalCliContext)


def stop_services(cli_context: LocalCliContext, delete_data):
    """Stop services."""
    if delete_data:
        delete_data = click.confirm(
            f'Do you want to remove all data associated with the local platform?({cli_context.do.host_data_directory})',
            abort=True)
    cli_context.sm.cleanup(delete_data)
    cli_context.do.cleanup(delete_data)


@cli.group(help="Commands related to managing the local platform")
@click.option('--run-as', default=None, help="Change the default user you run docker containers as. "
                                             "Useful is situations where you need to access docker with sudo. "
                                             "Example values are \"1000:1000\"")
@click.pass_context
def local(ctx, run_as):
    """Local command group.

    We create our local platform context here.
    """
    config = dict()
    if run_as:
        config['run_as'] = run_as

    ctx.obj = LocalCliContext(config)


@local.command()
@click.option("--delete-data/--no-delete-data", default=False)
@pass_do
def down(cli_context: LocalCliContext, delete_data):
    """Shutdown the local execution platform(and optionally delete data."""
    stop_services(cli_context, delete_data)


@local.command()
@click.option("--delete-data/--no-delete-data", help="SHold the local platform be deleted", default=False)
@pass_do
def stop(cli_context: LocalCliContext, delete_data):
    """Stop the local platform."""
    stop_services(cli_context, delete_data)


@local.command()
@pass_do
def start(cli_context: LocalCliContext):
    """Start the local execution platform."""
    cli_context.sm.create_services()
    try:
        time.sleep(4)
        import webbrowser
        from idmtools_platform_local.config import get_api_path
        webbrowser.open(get_api_path().replace("/api", ""))
    except Exception as e:
        click.echo(f"Could not open in web browser: {str(e)}")
        pass


@local.command()
@pass_do
def restart(cli_context: LocalCliContext):
    """Restart the local execution platform."""
    cli_context.sm.restart_all()


@local.command()
@click.option("--logs/--no-logs", default=False)
@click.option("--diff/--no-diff", default=False)
@click.option('--output-filename', default=None, help="Output filename")
@pass_do
def info(cli_context: LocalCliContext, logs: bool, diff: bool, output_filename: str):  # noqa: D103
    i = get_service_info(cli_context.sm, diff, logs)
    if output_filename is not None:
        with open(output_filename, 'w') as logout:
            logout.write(i)
    else:
        print(i)


@local.command()
@pass_do
def status(cli_context: LocalCliContext):
    """
    Check the status of the local execution platform.
    """
    for c in ['redis', 'postgres', 'workers']:
        container = cli_context.sm.get(c, create=False)
        container_status_text(stringcase.titlecase(c), container)


def container_status_text(name, container):
    """
    Print container status in color based on state.

    Args:
        name: Name to display
        container: Container to status

    Returns:
        None
    """
    if container:
        click.echo(
            f'{name: >10}: [{Fore.GREEN}{container.status}{Fore.RESET}] [{container.name: >17}] [{container.short_id}] [{container.labels}]')
    else:
        click.echo(f'{name: >10}: [{Fore.RED}down{Fore.RESET}]')
