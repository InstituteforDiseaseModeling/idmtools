from typing import Optional, Tuple, List, Dict, Any
from tabulate import tabulate


from idmtools_platform_local.cli.utils import colorize_status, urlize_data_path
from idmtools_platform_local.client.simulations_client import SimulationsClient
from idmtools_platform_local.config import API_PATH

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


def status(id: Optional[str], experiment_id: Optional[str], status: Optional[str],
           tags: Optional[List[Tuple[str, str]]]):
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
    from idmtools_cli.cli.utils import show_error
    try:
        simulations = SimulationsClient.get_all(id, experiment_id=experiment_id, status=status, tags=tags)
    except RuntimeError as e:
        show_error(e.args[0])

    simulations = list(map(lambda x: prettify_simulation(x), simulations))
    print(tabulate(simulations, headers='keys', tablefmt='psql', showindex=False))
