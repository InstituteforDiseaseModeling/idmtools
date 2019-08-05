import click
import stringcase as stringcase
from colorama import Fore
from idmtools_cli.cli import cli
from idmtools_platform_local.docker.DockerOperations import DockerOperations


@cli.group(help="Commands related to managing the local platform")
def local():
    pass


@local.command()
@click.option("--delete-data/--no-delete-data", default=False)
def down(delete_data):
    """Shutdown the local execution platform(and optionally delete data"""
    do = DockerOperations()
    click.confirm(f'Do you want to remove all data associated with the local platform?({do.host_data_directory})', abort=True)
    do.cleanup(delete_data)


@local.command()
def start():
    """Start the local execution platform"""
    do = DockerOperations()
    do.create_services()


@local.command()
def restart():
    """Restart the local execution platform"""
    do = DockerOperations()
    do.restart_all()


@local.command()
def status():
    """
    Check the status of the local execution platform
    """
    do = DockerOperations()
    for c in ['redis', 'postgres', 'workers']:
        container = getattr(do, f'get_{c}')()
        container_status_text(stringcase.titlecase(c), container)


def container_status_text(name, container):
    if container:
        click.echo(
            f'{name: >10}: [{Fore.GREEN}{container.status}{Fore.RESET}] [{container.name: >17}] [{container.short_id}] [{container.labels}]')
    else:
        click.echo(f'{name: >10}: [{Fore.RED}down{Fore.RESET}]')
