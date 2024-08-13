"""
Here we implement the ContainerPlatform status utils.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import os
from rich.console import Console
from typing import List, NoReturn
from logging import getLogger
from idmtools_platform_container.utils.general import normalize_path

logger = getLogger(__name__)
user_logger = getLogger('user')

#############################
# Check Status
#############################

status_mapping = {
    '0': 'SUCCEEDED',
    '100': 'RUNNING',
    '-1': 'FAILED'
}

FILE_NAME = 'job_status.txt'


def get_simulation_status(sim_path: str) -> str:
    """
    Get the status of a simulation.
    Args:
        sim_path: Simulation Directory Path
    Returns:
        simulation status
    """
    status_file_path = os.path.join(sim_path, FILE_NAME)

    if os.path.isfile(status_file_path):
        with open(status_file_path, 'r') as file:
            content = file.read().strip()

            status = status_mapping.get(content, 'Pending')
            return status
    else:
        return 'Pending'


def append_with_limit(lst: List, item: str, limit: int) -> List:
    """
    Append an item to a list with a limit.
    Args:
        lst: list of items
        item: item to be added
        limit: max number of items in the list
    Returns:
        list: updated list
    """
    if len(lst) < limit:
        lst.append(item)
    elif len(lst) == limit:
        lst.append('...')
    return lst


def summarize_status_files(exp_dir: str, max_display: int = 10, verbose: bool = False) -> NoReturn:
    """
    Summarize the status of simulations.
    Args:
        exp_dir: Experiment Directory Path
        max_display: the maximum number of items to display
        verbose: whether to display the simulation details
    Returns:
        None
    """
    summary = {
        'SUCCEEDED': [],
        'RUNNING': [],
        'FAILED': [],
        'PENDING': []
    }

    counter = {
        'SUCCEEDED': 0,
        'RUNNING': 0,
        'FAILED': 0,
        'PENDING': 0
    }

    total_simulation_count = 0

    # Traverse through all sub-folders in the given folder path
    for sub_folder in os.listdir(exp_dir):
        sub_folder_path = os.path.join(exp_dir, sub_folder)

        if os.path.isdir(sub_folder_path):
            # Check if the sub-folder contains metadata.json
            if not os.path.exists(os.path.join(sub_folder_path, 'metadata.json')):
                continue
            total_simulation_count += 1
            status_file_path = os.path.join(sub_folder_path, FILE_NAME)

            if os.path.isfile(status_file_path):
                with open(status_file_path, 'r') as file:
                    content = file.read().strip()

                    status = status_mapping.get(content, 'PENDING')
                    summary[status] = append_with_limit(summary[status], sub_folder, max_display)
                    counter[status] += 1
            else:
                summary['PENDING'] = append_with_limit(summary['PENDING'], sub_folder, max_display)
                counter['PENDING'] += 1

    # Print out the results
    console = Console()
    console.print(f'\n[bold][cyan]Experiment Directory[/][/]: \n{normalize_path(exp_dir)}\n')
    console.print(f"[bold][cyan]Simulation Count[/][/]: [yellow]{total_simulation_count}[/]\n")

    for status in ['SUCCEEDED', 'FAILED', 'RUNNING', 'PENDING']:
        # console.print(f"{status} ({counter[status]})")
        if status == 'SUCCEEDED':
            console.print(f"[bold][green]{status}[/][/] ({counter[status]})")
        elif status == 'FAILED':
            console.print(f"[bold][red]{status}[/][/] ({counter[status]})")
        elif status == 'RUNNING':
            console.print(f"[bold][cyan]{status}[/][/] ({counter[status]})")
        elif status == 'PENDING':
            console.print(f"[bold][grey69]{status}[/][/] ({counter[status]})")
        if verbose:
            for sim in summary[status]:
                console.print(f"{sim:>40}")
