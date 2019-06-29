from typing import Optional, Tuple, List, Any, Dict
import click
import requests
from tabulate import tabulate
from idmtools_local.cli.base import cli
from idmtools_local.cli.utils import parent_status_to_progress, urlize_data_path, tags_help, show_api_error
from idmtools_local.config import API_PATH


EXPERIMENTS_URL = f'{API_PATH}/experiments'


def prettify_experiment(experiment: Dict[str, Any]):
    """
    Prettifies a JSON Experiment object for printing on a console. This includes
    - Making a pretty progress bar
    - URL-ifying the data paths

    Args:
        experiment: JSON representation of the Experiment(from API)

    Returns:

    """
    experiment['progress'] = parent_status_to_progress(experiment['progress'])
    experiment['data_path'] = urlize_data_path(experiment['data_path'])
    return experiment


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

    response = requests.get(EXPERIMENTS_URL if id is None else (EXPERIMENTS_URL + '/' + id), params=dict(tag=tag))
    if response.status_code != 200:
        show_api_error(response)
    result = response.json()
    result = list(map(lambda x: prettify_experiment(x), result))
    print(tabulate(result, headers='keys', tablefmt='psql', showindex=False))


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
    print(f'Deleting Experiment: {id}')
    experiment_url = f'{EXPERIMENTS_URL}/{id}'
    response = requests.get(experiment_url)
    experiment_data = response.json()
    if not data or (data and
                    click.confirm('Deleting experiment data is irreversible. Are you sure you want to delete all '
                                  'experiment data?')):
        print(f'Deleting {experiment_data["data_path"]}')
        response = requests.delete(experiment_url, params=dict(data=data))
        if response.status_code == 204:
            print('Experiment removed successfully')
        else:
            show_api_error(response)



