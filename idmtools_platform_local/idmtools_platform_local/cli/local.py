import click
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
    do.restart_all()


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
    redis = do.get_redis()
    if redis:
        click.echo(f'Redis:      [{Fore.GREEN}{redis.status}{Fore.RESET}] [{redis.id}] ')
    else:
        click.echo(f'Redis:      [{Fore.RED}down{Fore.RESET}]')

    postgres = do.get_postgres()
    if postgres:
        click.echo(f'Postgres    [{Fore.GREEN}{postgres.status}{Fore.RESET}] [{postgres.id}] ')
    else:
        click.echo(f'Postgres:   [{Fore.RED}down{Fore.RESET}]')

    workers = do.get_workers()
    if workers:
        click.echo(f'Workers:    [{Fore.GREEN}{workers.status}{Fore.RESET}] [{workers.id}] ')
    else:
        click.echo(f'Workers:    [{Fore.RED}down{Fore.RESET}]')
