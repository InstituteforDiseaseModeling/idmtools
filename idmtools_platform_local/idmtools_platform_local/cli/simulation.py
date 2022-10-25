"""idmtools local platform simulation cli commands.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from typing import Optional, Tuple, List, Dict, Any

import requests
from tabulate import tabulate


from idmtools_platform_local.cli.utils import colorize_status, urlize_data_path
from idmtools_platform_local.client.simulations_client import SimulationsClient
from idmtools_platform_local.config import API_PATH

SIMULATIONS_URL = f'{API_PATH}/simulations'


def prettify_simulation(simulation: Dict[str, Any]):
    """
    Prettifies a JSON Simulation object for printing on a console.

    This includes
    - Making a pretty progress bar
    - URL-ifying the data paths

    Args:
        simulation: JSON representation of the Experiment(from API)

    Returns:
        Prettified simulation
    """
    simulation['status'] = colorize_status(simulation['status'])
    simulation['data_path'] = urlize_data_path(simulation['data_path'])
    column_order = ("simulation_uid", "experiment_id", "status", "created", "tags", "extra_details", "updated", "data_path")
    return {co: simulation[co] for co in column_order}


def status(id: Optional[str], experiment_id: Optional[str], status: Optional[str],
           tags: Optional[List[Tuple[str, str]]]):
    """
    List of statuses for simulation(s) with the ability to filter by id, experiment_id, status, and tags.

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
        if id is None:
            simulations = SimulationsClient.get_all(status=status, tags=tags, per_page=100)
        else:
            simulations = [SimulationsClient.get_one(id, status=status, tags=tags)]
        simulations = list(map(lambda x: prettify_simulation(x), simulations))
        print(tabulate(simulations, headers='keys', tablefmt='psql', showindex=False))
    except RuntimeError as e:
        show_error(e.args[0])
    except requests.exceptions.ConnectionError as e:
        show_error(f"Could not connect to the local platform: {e.request.url}. Is the local platform running?")
