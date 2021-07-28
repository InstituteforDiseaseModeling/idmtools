"""idmtools cli experiment tools.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from typing import Optional, Tuple, List, Any, Dict
import click
import requests
from tabulate import tabulate

from idmtools_platform_local.cli.utils import parent_status_to_progress, urlize_data_path
from idmtools_platform_local.client.experiments_client import ExperimentsClient
from idmtools_platform_local.config import API_PATH

EXPERIMENTS_URL = f'{API_PATH}/experiments'


def prettify_experiment(experiment: Dict[str, Any]):
    """
    Prettifies a JSON Experiment object for printing on a console.

    This includes
    - Making a pretty progress bar
    - URL-ifying the data paths
    - sorting the columns

    Args:
        experiment: JSON representation of the Experiment(from API)

    Returns:
        Prettify experiment
    """
    experiment['progress'] = parent_status_to_progress(experiment['progress'])
    experiment['data_path'] = urlize_data_path(experiment['data_path'])
    column_order = ("experiment_id", "created", "progress", "tags", "extra_details", "updated", "data_path")
    return {co: experiment[co] for co in column_order}


def status(id: Optional[str], tags: Optional[List[Tuple[str, str]]]):
    """
    List the status of experiment(s) with the ability to filter by experiment id and tags.

    Args:
        id (Optional[str]): Optional ID of the experiment you want to filter by
        tags (Optional[List[Tuple[str, str]]]): Optional list of tuples in form of tag_name tag_value to user to filter
            experiments with
    """
    from idmtools_cli.cli.utils import show_error
    try:
        if id is None:
            experiments = ExperimentsClient.get_all(tags=tags, per_page=100)
        else:
            experiments = ExperimentsClient.get_one(id, tags=tags)
            experiments = [experiments]
        experiments = list(map(lambda x: prettify_experiment(x), experiments))
        print(tabulate(experiments, headers='keys', tablefmt='psql', showindex=False))
    except RuntimeError as e:
        show_error(e.args[0])
    except requests.exceptions.ConnectionError as e:
        show_error(f"Could not connect to the local platform: {e.request.url}. Is the local platform running?")


def extra_commands():
    """This ensures our local platform specific commands are loaded."""
    from idmtools_cli.cli.experiment import experiment
    from idmtools_cli.cli.utils import show_error
    import idmtools_platform_local.cli.local  # noqa: 40F1

    @experiment.command(help="Delete an experiment, and optionally, its data")
    @click.argument('experiment_id')
    @click.option('--data/--no-data', default=False, help="Should we delete the data as well?")
    def delete(experiment_id: str, data: bool):
        """
        Delete an experiment, and optionally, its data.

        Args:
            experiment_id (str): ID of exp to delete
            data (bool): If true, specifies data folder for experiment should be deleted, otherwise it will be kept
        """
        print(f'Deleting Experiment: {experiment_id}')
        exp: Dict = None
        try:
            exp = ExperimentsClient.get_one(experiment_id)
        except RuntimeError as e:
            show_error(e.args[0])

        # Check with user they really want to delete data
        if (data and click.confirm('Deleting exp data is irreversible. '
                                   'Are you sure you want to delete all exp data?')):
            data = True
            print(f'Deleting {exp["data_path"]}')
        elif data:
            data = False

        try:
            response = ExperimentsClient.delete(experiment_id, data)
            if response:
                print('Experiment removed successfully')
        except RuntimeError as e:
            show_error(e.args[0])
