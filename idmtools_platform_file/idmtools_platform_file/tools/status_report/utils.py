"""
Utility functions used by File Platform.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import os
import shutil
from pathlib import Path
from logging import getLogger
from typing import Dict, Tuple, TYPE_CHECKING
from idmtools.core import ItemType

if TYPE_CHECKING:  # pragma: no cover
    from idmtools.entities.iplatform import IPlatform

user_logger = getLogger('user')

EXPERIMENT_FILES = ['stdout.txt', 'stderr.txt']
SIMULATION_FILES = ['stdout.txt', 'stderr.txt', 'job_status.txt']


def get_latest_experiment(platform: 'IPlatform') -> Dict:
    """
    Find the latest experiment.
    Args:
        platform: Platform
    Returns:
        Dictionary with experiment info
    """
    try:
        # take the last suite as the search scope
        last_suite_dir = max(Path(platform.job_directory).glob('*/'), key=os.path.getmtime)
        batch_dir = max(Path(last_suite_dir).glob('*/batch.sh'), key=os.path.getmtime)
        exp_dir = Path(batch_dir).parent
        exp_id = exp_dir.name
        suite_id = exp_dir.parent.name

        r = dict(suite_id=suite_id, experiment_id=exp_id, experiment_directory=str(exp_dir),
                 job_directory=str(platform.job_directory))
        return r
    except:
        raise FileNotFoundError("Could not find the last Experiment")


def check_status(platform: 'IPlatform', exp_id: str = None, display: bool = False) -> None:
    """
    List simulations status.
    Args:
        platform: Platform
        exp_id: experiment id
        display: True/False
    Returns:
        None
    """
    if exp_id is None:
        exp_dic = get_latest_experiment(platform)
        exp_id = exp_dic['experiment_id']

    _exp = platform.get_item(exp_id, ItemType.EXPERIMENT)
    print(_exp)

    _pending = []
    _running = []
    _failed = []
    _succeeded = []
    _simulations = _exp.simulations
    for sim in _simulations:
        sim_dir = platform.get_directory(sim)
        job_status_path = sim_dir.joinpath("job_status.txt")
        if not job_status_path.exists():
            _pending.append(f"    {sim.id}")
        else:
            status = open(job_status_path).read().strip()
            if status == '0':
                _succeeded.append(f"    {sim.id}")
            elif status == '100':
                _running.append(f"    {sim.id}")
            elif status == '-1':
                _failed.append(f"    {sim.id}")
            else:
                _running.append(f"    {sim.id}")

    # Output report
    user_logger.info(f"\n{'Simulation Count: '.ljust(20)} {len(_simulations)}\n")

    user_logger.info(f'SUCCEEDED ({len(_succeeded)})')
    if display:
        user_logger.info('\n'.join(_succeeded))

    user_logger.info(f'FAILED ({len(_failed)})')
    if display:
        user_logger.info('\n'.join(_failed))

    user_logger.info(f'RUNNING ({len(_running)})')
    if display:
        user_logger.info('\n'.join(_running))

    user_logger.info(f'PENDING ({len(_pending)})')
    if display:
        user_logger.info('\n'.join(_pending))

    if _exp.status is None:
        user_logger.info(f'\nExperiment Status: {None}')
    else:
        user_logger.info(f'\nExperiment Status: {_exp.status.name}\n')


def clear_history(platform: 'IPlatform', exp_id: str = None, sim_id: Tuple = None, remove_list=None) -> None:
    """
    Clear the history files generated from running experiment.
    Args:
        platform: Platform
        exp_id: experiment id
        sim_id: simulation id
        remove_list: list of files/folders
    Returns:
        None
    """

    def _clear_simulation(sim_id, remove_list):
        sim_dir = platform.get_directory_by_id(sim_id, ItemType.SIMULATION)
        for fi in SIMULATION_FILES + list(remove_list):
            if sim_dir.joinpath(fi).exists():
                if sim_dir.joinpath(fi).is_dir():
                    shutil.rmtree(sim_dir.joinpath(fi))
                else:
                    sim_dir.joinpath(fi).unlink(missing_ok=True)

    if sim_id is not None and len(sim_id) > 0:
        for sid in sim_id:
            _clear_simulation(sid, remove_list)
    elif exp_id is not None:
        exp = platform.get_item(exp_id, ItemType.EXPERIMENT)
        exp_dir = platform.get_directory(exp)

        # Delete generated files from experiment past run
        for fi in EXPERIMENT_FILES:
            if exp_dir.joinpath(fi).exists():
                if exp_dir.joinpath(fi).is_dir():
                    shutil.rmtree(exp_dir.joinpath(fi))
                else:
                    exp_dir.joinpath(fi).unlink(missing_ok=True)

        # Delete generated files from simulations
        for sim in exp.simulations:
            _clear_simulation(sim.id, remove_list)
    else:
        user_logger.warning("Must provide exp_id or sim_id!")
        exit(-1)
