import click

from idmtools_cli.cli import cli
from idmtools_platform_local.docker.DockerOperations import DockerOperations


@cli.group(help="Commands related to managing the local platform")
def local():
    pass


@local.command()
@click.option("--delete-data/--no-delete-data", default=False)
def down(delete_data):
    do = DockerOperations()
    click.confirm(f'Do you want to remove all data associated with the local platform?({do.host_data_directory})', abort=True)
    do.cleanup(delete_data)


@local.command()
def restart():
    do = DockerOperations()
    do.restart_all()


@local.command()
def status():
    do = DockerOperations()
    redis = do.get_redis()
    if redis:
        print(f'Redis running in container: {redis.id}')

    postgres = do.get_postgres()
    if postgres:
        print(f'Postgres running in container: {postgres.id}')

    workers = do.get_workers()
    if workers:
        print(f'Worker running in container: {workers.id}')
