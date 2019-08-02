from typing import Optional, Tuple, List, Any, Dict
import click
from tabulate import tabulate

from idmtools_cli.cli.utils import show_error
from idmtools_platform_local.cli.utils import parent_status_to_progress, urlize_data_path
from idmtools_platform_local.client.experiments_client import ExperimentsClient
from idmtools_platform_local.config import API_PATH

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


def status(id: Optional[str], tags: Optional[List[Tuple[str, str]]]):
    """
    List the status of experiment(s) with the ability to filter by experiment id and tags

    Args:
        id (Optional[str]): Optional ID of the experiment you want to filter by
        tag (Optional[List[Tuple[str, str]]]): Optional list of tuples in form of tag_name tag_value to user to filter
            experiments with
    """
    try:
        experiments = ExperimentsClient.get_all(id, tags=tags)
    except RuntimeError as e:
        show_error(e.args[0])
    experiments = list(map(lambda x: prettify_experiment(x), experiments))
    print(tabulate(experiments, headers='keys', tablefmt='psql', showindex=False))


def extra_commands():
    """ This ensures our local platform specific commands are loaded
    """
    from idmtools_cli.cli.experiment import experiment
    @experiment.command()
    @click.argument('id')
    @click.option('--data/--no-data', default=False, help="Should we delete the data as well?")
    def delete(id: str, data: bool):
        """
        Delete an experiment, and optionally, its data

        Args:
            id (str): ID of exp to delete
            data (bool): If true, specifies data folder for experiment should be deleted, otherwise it will be kept
        """
        print(f'Deleting Experiment: {id}')
        exp: Dict = None
        try:
            exp = ExperimentsClient.get_all(id)
        except RuntimeError as e:
            show_error(e.args[0])

        if not data or (data and click.confirm('Deleting exp data is irreversible. '
                                               'Are you sure you want to delete all exp data?')):
            print(f'Deleting {exp["data_path"]}')
            try:
                response = ExperimentsClient.delete(id, data)
                if response:
                    print('Experiment removed successfully')
            except RuntimeError as e:
                show_error(e.args[0])
