import shutil
import sys
from typing import Optional, Tuple, List
import click
import pandas as pd
from sqlalchemy import func, String, or_
from tabulate import tabulate
from idmtools_local.cli.base import cli
from idmtools_local.cli.utils import parent_status_to_progress, urlize_data_path, tags_help
from idmtools_local.data.job_status import JobStatus
from idmtools_local.database import get_session


@cli.group(help="Commands related to experiments(top-level jobs)")
def experiment():
    """
    Create the sub-command experiment under the main cli command
    """
    pass


@experiment.command()
@click.option('--id', default=None, help="Filter status by experiment ID")
@click.option('--tag', default=None, nargs=2, multiple=True, help=tags_help)
def status(id: Optional[str], tag: Optional[List[Tuple[str, str]]]):
    """
    List the status of experiment(s) with the ability to filter by experiment id and tags

    Args:
        id (Optional[str]): Optional ID of the experiment you want to filter by
        tag (Optional[List[Tuple[str, str]]]): Optional list of tuples in form of tag_name tag_value to user to filter
            experiments with
    """
    session = get_session()
    # experiments don't have parents
    criteria=[JobStatus.parent_uuid == None]

    # start builder our optional criteria
    if id is not None:
        criteria.append(JobStatus.uuid == id)

    if tag is not None:
        for tag in tag:
            criteria.append((JobStatus.tags[tag[0]].astext.cast(String) == tag[1]))

    query = session.query(JobStatus).filter(*criteria).order_by(JobStatus.uuid.desc())

    # Pull our experiment status into a dataframe
    df = pd.read_sql(query.statement, query.session.bind, columns=['uuid', 'status', 'data_path', 'tags'])

    # this will fetch the overall progress of the simulations(sub jobs) for the experiments
    subjob_status_query = session.query(JobStatus.parent_uuid, JobStatus.status,
                                         func.count(JobStatus.status).label("total"))\
        .filter(JobStatus.parent_uuid != None).group_by(JobStatus.parent_uuid, JobStatus.status)

    sdf = pd.read_sql(subjob_status_query.statement, subjob_status_query.session.bind, index_col=['parent_uuid'])

    # There may be a better way to do this merge of data. For now the loop works
    # basically we are building the progress bar for each experiment based on the simulation statuses
    status_bars = []
    for job in df['uuid']:
        job_status=dict()
        job_list = sdf.loc[job]
        # since we index by parent_uuid, if could have multiple rows. This is the general case(most experiments will
        # have simulations is different statuses at some point) so we convert any results that are a single row
        # from their series form to the transposed dataframe that we get in the general case
        if type(job_list) is pd.Series:
            job_list = job_list.to_frame().transpose()
        # now build our status object
        for idx, row in job_list.iterrows():
            job_status[row['status']] = row['total']
        # and make a pretty progress bar
        status_bars.append(parent_status_to_progress(job_status))
    df.insert(1, 'progress', status_bars)
    df['data_path'] = df['data_path'].apply(urlize_data_path)

    # we don't need status or parent_uuid or status(now that we have progress bars) for experiments. Let's drop those
    df.drop(columns=['parent_uuid', 'status'], inplace=True)
    # and let's rename columns to make it more clear fo user what they are looking at
    df.rename(index=str, columns=dict(uuid='experiment_id'), inplace=True)

    print(tabulate(df, headers='keys', tablefmt='psql', showindex=False))


@experiment.command()
@click.argument('id')
@click.option('--data/--no-data', default=False, help="Should we delete the data as well?")
def delete(id: str, data: bool):
    """
    Delete an experiment, and optionally, its data

    Args:
        id (str): ID of experiment to delete
        data (bool): If true, specifies data folder for experiment should be deleted, otherwise it will be kept
    """
    session = get_session()

    job:JobStatus = session.query(JobStatus).filter(JobStatus.uuid == id).first()
    if job is None:
        print(f'Error: No experiment with id of {id}')
        sys.exit(-1)

    if data and click.confirm('Deleting experiment data is irreversible. Are you sure you want to delete all '
                              'experimental data?'):
        print(f'Deleting {job.data_path}')
        try:
            shutil.rmtree(job.data_path)
        except FileNotFoundError:
            # we will assume it has been cleaned up manually
            pass
    session.query(JobStatus).filter( or_(JobStatus.uuid == id, JobStatus.parent_uuid == id)).delete()
    session.commit()
