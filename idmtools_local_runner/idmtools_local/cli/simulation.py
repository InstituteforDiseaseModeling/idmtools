from typing import Optional, Tuple, List, Dict, Any
import click
from tabulate import tabulate
from idmtools_local.cli.base import cli
from idmtools_local.cli.utils import colorize_status, tags_help, urlize_data_path, show_error
from idmtools_local.client.simulations_client import SimulationsClient
from idmtools_local.config import API_PATH
from idmtools_local.status import Status

SIMULATIONS_URL = f'{API_PATH}/simulations'


def prettify_simulation(simulation: Dict[str, Any]):
    """
    Prettifies a JSON Simulation object for printing on a console. This includes
    - Making a pretty progress bar
    - URL-ifying the data paths

    Args:
        simulation: JSON representation of the Experiment(from API)

    Returns:

    """
    simulation['status'] = colorize_status(simulation['status'])
    simulation['data_path'] = urlize_data_path(simulation['data_path'])
    return simulation


@cli.group(help="Commands related to simulations(sub-level jobs)")
def simulation():
    """
    Defines our simulation sub-command group
    Returns:

    """
    pass


@simulation.command()
@click.option('--id', default=None, help="Filter status by simulation ID")
@click.option('--experiment-id', default=None, help="Filter status by experiment ID")
@click.option('--status', default=None, type=click.Choice([e.value for e in Status]))
@click.option('--tag', default=None, nargs=2, multiple=True, help=tags_help)
def status(id: Optional[str], experiment_id: Optional[str], status: Optional[str],
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
    try:
        simulations = SimulationsClient.get_all(id, experiment_id=experiment_id, status=status, tag=tag)
    except RuntimeError as e:
        show_error(e.args[0])

    simulations = list(map(lambda x: prettify_simulation(x), simulations))
    print(tabulate(simulations, headers='keys', tablefmt='psql', showindex=False))

