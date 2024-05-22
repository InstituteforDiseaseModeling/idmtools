"""idmtools scheduling utils for comps.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import json
from os import PathLike
from typing import List, Union, Dict
from idmtools.assets import Asset
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools.entities.templated_simulation import TemplatedSimulations
from logging import DEBUG
import logging

SCHEDULING_ERROR_UNSUPPORTED_TYPE = "The method only support object type: Experiment, Simulation, TemplatedSimulations!"
SCHEDULING_ERROR_EMPTY_EXPERIMENT = "You cannot add scheduling config to an empty experiment."

logger = logging.getLogger(__name__)


def default_add_workorder_sweep_callback(simulation, file_name, file_path):
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


def default_add_schedule_config_sweep_callback(simulation, command: str = None, node_group_name: str = None,
                                               num_cores: int = 1, **config_opts):
    """Default callback to be used for sweeps that affect a scheduling config."""
    add_schedule_config(simulation, command=command, node_group_name=node_group_name, num_cores=num_cores,
                        **config_opts["config_opts"])


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


def _add_work_order_asset(item: Union[Experiment, Simulation, TemplatedSimulations], config: Dict,
                          file_name: str = "WorkOrder.json"):
    """
    Helper function to add an WorkOrder.json asset to an item.

    Args:
        item: The item to add the asset to
        config: The configuration dictionary
        file_name: The name of the file to create

    Returns:
        None
    """

    def _process_simulation(simulation: Simulation):
        setattr(simulation, 'scheduling', True)
        if hasattr(simulation.task.command, 'cmd') and len(simulation.task.command.cmd) > 0:
            config["Command"] = simulation.task.command.cmd
        ctn = json.dumps(config, indent=3)
        simulation.task.transient_assets.add_asset(Asset(filename=file_name, content=ctn))

    if isinstance(item, Simulation):
        _process_simulation(item)
    elif isinstance(item, TemplatedSimulations):
        _process_simulation(item.base_simulation)
    elif isinstance(item, Experiment):
        if isinstance(item.simulations.items, TemplatedSimulations):
            if len(item.simulations.items) == 0:
                raise ValueError(SCHEDULING_ERROR_EMPTY_EXPERIMENT)
            if logger.isEnabledFor(DEBUG):
                logger.debug("Using Base task from template for WorkOrder.json assets")
            _process_simulation(item.simulations.items.base_simulation)
            for sim in item.simulations.items.extra_simulations():
                _process_simulation(sim)
        elif isinstance(item.simulations.items, List):
            if len(item.simulations.items) == 0:
                raise ValueError(SCHEDULING_ERROR_EMPTY_EXPERIMENT)
            if logger.isEnabledFor(DEBUG):
                logger.debug("Using all tasks to gather assets")
            for sim in item.simulations.items:
                _process_simulation(sim)
        else:
            raise ValueError("You cannot run an empty experiment")
    else:
        raise ValueError(SCHEDULING_ERROR_UNSUPPORTED_TYPE)


def add_work_order(item: Union[Experiment, Simulation, TemplatedSimulations], file_name: str = "WorkOrder.json",
                   file_path: Union[str, PathLike] = "./WorkOrder.json"):
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
    with open(str(file_path), "r") as jsonFile:
        config = json.loads(jsonFile.read())
    _add_work_order_asset(item, config, file_name=file_name)


def add_schedule_config(item: Union[Experiment, Simulation, TemplatedSimulations], command: str = None,
                        node_group_name: str = None, num_cores: int = 1, **config_opts):
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
        - TODO refactor to reuse the add_work_order if possible. The complication is simulation command possibly
    """
    config = dict(Command=command, NodeGroupName=node_group_name, NumCores=num_cores)
    config.update(config_opts)
    _add_work_order_asset(item, config, file_name="WorkOrder.json")
