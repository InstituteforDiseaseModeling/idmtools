import click
from colorama import init
import pandas as pd
from tabulate import tabulate
from idmtools_local.data import SimulationDatabase, Status


@click.group()
def cli():
    pass


@cli.command()
@click.option('--experiment', default=None, help="Filter status by experiment ID")
@click.option('--simulation', default=None, help="Filter status by simulation ID")
@click.option('--status', default=None, type=click.Choice(['md5', 'sha1']))
def status(experiment, simulation, status):
    df = pd.DataFrame(columns=['parent_uuid',  'uid', 'status', 'tags', 'data_path'])

    cache = SimulationDatabase._open_cache()
    for k in cache.iterkeys():
        if (experiment is None and simulation is None) or \
                (experiment is not None and cache[k].parent_uuid == experiment) or \
                (simulation is not None and cache[k].uid == simulation):
            row= cache[k].__dict__
            if row['status'] == Status.failed:
                row['status'] = '\033[31m' + str(row['status']) + '\033[30m'
            elif row['status'] == Status.done:
                row['status'] = '\033[32m' + str(row['status']) + '\033[30m'
            else:
                row['status'] = str(row['status'])
            df = df.append(cache[k].__dict__, ignore_index=True)

    df.sort_values(by=['parent_uuid', 'uid'], inplace=True)
    df.rename(index=str, columns=dict(parent_uuid='experiment_uid', uid='simulation_uid'))
    print(tabulate(df, headers='keys', tablefmt='psql', showindex=False))


if __name__ == '__main__':
    init()
    cli()