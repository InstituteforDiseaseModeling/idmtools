"""idmtools scheduling utils for comps.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import json
from os import PathLike
from typing import List, Union
from idmtools.assets import Asset
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools.entities.templated_simulation import TemplatedSimulations
from logging import DEBUG
import logging

SCHEDULING_ERROR_UNSUPPORTED_TYPE = "The method only support object type: Experiment, Simulation, TemplatedSimulations!"
SCHEDULING_ERROR_EMPTY_EXPERIMENT = "You cannot add scheduling config to an empty experiment."

logger = logging.getLogger(__name__)


def default_add_workerorder_sweep_callback(simulation, file_name, file_path):
    """
    Utility function to add updated WorkOrder.json to each simulation as linked file via simulation task.

    first loads original workorder file from local, then update Command field in it from each simulation object's
    simulation.task.command.cmd, then write updated command to WorkOrder.json, and load this file to simulation

    Args:
        simulation: Simulation we are configuring
        file_name: Filename to use
        file_path: Path to file

    Returns:
        None
    """
    add_work_order(simulation, file_name=file_name, file_path=file_path)


def default_add_schedule_config_sweep_callback(simulation, command: str = None, node_group_name: str = 'idm_cd', num_cores: int = 1, **config_opts):
    """Default callback to be used for sweeps that affect a scheduling config."""
    add_schedule_config(simulation, command=command, node_group_name=node_group_name, num_cores=num_cores, **config_opts["config_opts"])


def scheduled(simulation: Simulation):
    """
    Determine if scheduling is defined on the simulation.

    Args:
        simulation: Simulation to check

    Returns:
        True if simulation.scheduling is defined and true.
    """
    scheduling = getattr(simulation, 'scheduling', False)
    return scheduling


def _add_work_order_asset(_simulation: Simulation, _file_name: str = "WorkOrder.json", _file_path: Union[str, PathLike] = "./WorkOrder.json", _update: bool = True):
    """
    Add work order asset to a simulation.

    Args:
        _simulation: Simulation to add workorder to
        _file_name: Filename to use
        _file_path: Path to workorder file
        _update: Update workorder using command from simulation

    Returns:
        None

    Notes:
        - TODO combine with _add_schedule_config_asset. The only real difference if loading the json file, which would could do outside of this method
    """
    if scheduled(_simulation):
        return

    with open(str(_file_path), "r") as jsonFile:
        _config = json.loads(jsonFile.read())

    if _update and len(_simulation.task.command.cmd) > 0:
        _config["Command"] = _simulation.task.command.cmd

    ctn = json.dumps(_config, indent=3)
    _simulation.task.transient_assets.add_asset(Asset(filename=_file_name, content=ctn))
    setattr(_simulation, 'scheduling', True)


def add_work_order(item: Union[Experiment, Simulation, TemplatedSimulations], file_name: str = "WorkOrder.json", file_path: Union[str, PathLike] = "./WorkOrder.json"):
    """
    Adds workorder.json.

    Args:
        item: Item to add work order to
        file_name: Workorder file name
        file_path: Path to file(locally)

    Returns:
        None

    Raises:
        ValueError - If experiment is empty
                     If item is not an experiment, simulation, or TemplatedSimulations
    """
    if isinstance(item, Simulation):
        _add_work_order_asset(item, _file_name=file_name, _file_path=file_path, _update=True)
    elif isinstance(item, TemplatedSimulations):
        _add_work_order_asset(item.base_simulation, _file_name=file_name, _file_path=file_path, _update=False)
    elif isinstance(item, Experiment):
        if isinstance(item.simulations.items, TemplatedSimulations):
            if len(item.simulations.items) == 0:
                raise ValueError(SCHEDULING_ERROR_EMPTY_EXPERIMENT)
            if logger.isEnabledFor(DEBUG):
                logger.debug("Using Base task from template for WorkOrder.json assets")
            _add_work_order_asset(item.simulations.items.base_simulation, _file_name=file_name, _file_path=file_path,
                                  _update=False)
            for sim in item.simulations.items.extra_simulations():
                _add_work_order_asset(sim, _file_name=file_name, _file_path=file_path, _update=True)
        elif isinstance(item.simulations.items, List):
            if len(item.simulations.items) == 0:
                raise ValueError(SCHEDULING_ERROR_EMPTY_EXPERIMENT)
            if logger.isEnabledFor(DEBUG):
                logger.debug("Using all tasks to gather assets")
            for sim in item.simulations.items:
                _add_work_order_asset(sim, _file_name=file_name, _file_path=file_path, _update=True)
        elif isinstance(item.simulations.items, List) and len(item.simulations.items) == 0:
            raise ValueError("You cannot run an empty experiment")
    else:
        raise ValueError(SCHEDULING_ERROR_UNSUPPORTED_TYPE)


def _add_schedule_config_asset(_simulation: Simulation, _config: dict, _update: bool = True):
    """
    Method to add scheduling config to simulation.

    If update is true, we pull the command from the simulation.

    Args:
        _simulation: Simulation to add scheduling config to
        _config: Config to use in workorder
        _update: When true and simulation has a command, we try to use that in our workorder

    Returns:
        None
    """
    if scheduled(_simulation):
        return

    if _update and len(_simulation.task.command.cmd) > 0:
        _config["Command"] = _simulation.task.command.cmd

    ctn = json.dumps(_config, indent=3)
    _simulation.task.transient_assets.add_asset(Asset(filename="WorkOrder.json", content=ctn))
    setattr(_simulation, 'scheduling', True)


def add_schedule_config(item: Union[Experiment, Simulation, TemplatedSimulations], command: str = None, node_group_name: str = 'idm_cd', num_cores: int = 1, **config_opts):
    """
    Add scheduling config to an Item.

    Scheduling config supports adding to Experiments, Simulations, and TemplatedSimulations

    Args:
        item: Item to add scheduling config to
        command: Command to run
        node_group_name: Node group name
        num_cores: Num of cores to use
        **config_opts: Additional config options

    Returns:
        None

    Raises:
        ValueError - If experiment is empty
                     If item is not an experiment, simulation, or TemplatedSimulations

    Notes:
        - TODO refactor to resuse the add_work_order if possible. The complication is simulation command possibly
    """
    config = dict(Command=command, NodeGroupName=node_group_name, NumCores=num_cores)
    config.update(config_opts)

    if isinstance(item, Simulation):
        _add_schedule_config_asset(item, _config=config, _update=True)
    elif isinstance(item, TemplatedSimulations):
        _add_schedule_config_asset(item.base_simulation, _config=config, _update=False)
    elif isinstance(item, Experiment):
        if isinstance(item.simulations.items, TemplatedSimulations):
            if len(item.simulations.items) == 0:
                raise ValueError(SCHEDULING_ERROR_EMPTY_EXPERIMENT)
            if logger.isEnabledFor(DEBUG):
                logger.debug("Using Base task from template for WorkOrder.json assets")
            _add_schedule_config_asset(item.simulations.items.base_simulation, _config=config, _update=False)
            for sim in item.simulations.items.extra_simulations():
                _add_schedule_config_asset(sim, _config=config, _update=True)
        elif isinstance(item.simulations.items, List):
            if len(item.simulations.items) == 0:
                raise ValueError(SCHEDULING_ERROR_EMPTY_EXPERIMENT)
            if logger.isEnabledFor(DEBUG):
                logger.debug("Using all tasks to gather assets")
            for sim in item.simulations.items:
                _add_schedule_config_asset(sim, _config=config, _update=True)
        elif isinstance(item.simulations.items, List) and len(item.simulations.items) == 0:
            raise ValueError(SCHEDULING_ERROR_EMPTY_EXPERIMENT)
    else:
        raise ValueError(SCHEDULING_ERROR_UNSUPPORTED_TYPE)
