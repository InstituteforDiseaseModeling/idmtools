import click
import stringcase as stringcase
from colorama import Fore
from idmtools_cli.cli import cli
from idmtools_platform_local.docker.DockerOperations import DockerOperations


pass_do = click.make_pass_decorator(DockerOperations)


@cli.group(help="Commands related to managing the local platform")
@click.option('--run-as', default=None, help="Change the default user you run docker containers as. "
                                             "Useful is situations where you need to access docker with sudo. "
                                             "Example values are \"1000:1000\"")
@click.pass_context
def local(ctx, run_as):
    config = dict()
    if run_as:
        config['run_as'] = run_as
    do = DockerOperations(**config)
    ctx.obj = do


@local.command()
@click.option("--delete-data/--no-delete-data", default=False)
@pass_do
def down(do: DockerOperations, delete_data):
    """Shutdown the local execution platform(and optionally delete data"""
    click.confirm(f'Do you want to remove all data associated with the local platform?({do.host_data_directory})', abort=True)
    do.cleanup(delete_data)


@local.command()
@pass_do
def start(do: DockerOperations):
    """Start the local execution platform"""
    do.create_services()


@local.command()
@pass_do
def restart(do: DockerOperations):
    """Restart the local execution platform"""
    do.restart_all()


@local.command()
@pass_do
def status(do: DockerOperations):
    """
    Check the status of the local execution platform
    """
    for c in ['redis', 'postgres', 'workers']:
        container = getattr(do, f'get_{c}')(False)
        container_status_text(stringcase.titlecase(c), container)


def container_status_text(name, container):
    if container:
        click.echo(
            f'{name: >10}: [{Fore.GREEN}{container.status}{Fore.RESET}] [{container.name: >17}] [{container.short_id}] [{container.labels}]')
    else:
        click.echo(f'{name: >10}: [{Fore.RED}down{Fore.RESET}]')
