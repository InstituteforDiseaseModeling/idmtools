from typing import Optional, Tuple, List
import click
import pandas as pd
from sqlalchemy import String
from tabulate import tabulate
from idmtools_local.cli.base import cli
from idmtools_local.cli.utils import colorize_status, tags_help, urlize_data_path
from idmtools_local.data.job_status import JobStatus, Status
from idmtools_local.database import get_session


@cli.group(help="Commands related to simulations(sub-level jobs)")
def simulation():
    """
    Defines our simulation sub-command group
    Returns:

    """
    pass


@simulation.command(name='status')
@click.option('--id', default=None, help="Filter status by simulation ID")
@click.option('--experiment-id', default=None, help="Filter status by experiment ID")
@click.option('--status', default=None, type=click.Choice([e.value for e in Status]))
@click.option('--tag', default=None, nargs=2, multiple=True, help=tags_help)
def sim_status(id: Optional[str], experiment_id: Optional[str], status: Optional[str],
               tag: Optional[List[Tuple[str, str]]]):
    """
    List of statuses for simulation(s) with the ability to filter by id, experiment_id, status, and tags

    Args:
        id (Optional[str]): Optional Id of simulation
        experiment_id (Optional[str]): Optional experiment id
        status (Optional[str]): Optional status string to filter by
        tag (Optional[List[Tuple[str, str]]]): Optional list of tuples in form of tag_name tag_value to user to filter
            experiments with

    Returns:
        None
    """
    session = get_session()
    # Simulations ALWAYS have a parent
    criteria = [JobStatus.parent_uuid != None]

    # start building our filter criteria
    if id is not None:
        criteria.append(JobStatus.uuid == id)

    if experiment_id is not None:
        criteria.append(JobStatus.parent_uuid == experiment_id)

    if status is not None:
        criteria.append(JobStatus.status == Status[status])

    if tag is not None:
        for tag in tag:
            criteria.append((JobStatus.tags[tag[0]].astext.cast(String) == tag[1]))

    query = session.query(JobStatus).filter(*criteria).order_by(JobStatus.uuid.desc(), JobStatus.parent_uuid.desc())

    # convert the result to dataframe
    df = pd.read_sql(query.statement, query.session.bind, columns=['uuid', 'status', 'data_path', 'tags'])

    # rename columns to be a bit clearer what the user is looking at
    df.rename(index=str, columns=dict(uuid='simulation_uid', parent_uuid='experiment_id'))

    # urlize the data paths
    df['data_path'] = df['data_path'].apply(urlize_data_path)
    # colorize the status text
    df['status'] = df['status'].apply(colorize_status)

    print(tabulate(df, headers='keys', tablefmt='psql', showindex=False))
