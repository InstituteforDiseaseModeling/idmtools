"""idmtools scheduling utils for comps.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import json
from os import PathLike
from typing import List, Union, Dict, Optional
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


def default_add_schedule_config_sweep_callback(
    simulation,
    command: str = None,
    NodeGroupName: Optional[str] = None,    # COMPS Windows HPC or COMPS Slurm
    NumCores: Optional[int] = None,         # COMPS Windows HPC or COMPS Slurm
    NumNodes: Optional[int] = None,         # COMPS Slurm only
    NumProcesses: Optional[int] = None,     # COMPS Slurm only
    EnableMpi: Optional[bool] = None,       # COMPS Slurm only
    Environment: Optional[dict] = None,     # COMPS Slurm only
    SingleNode: Optional[bool] = None,      # COMPS Windows HPC only
    Exclusive: Optional[bool] = None        # COMPS Windows HPC only
):
    """Default callback to be used for sweeps that affect a scheduling config."""
    add_schedule_config(
        simulation,
        command=command,
        NodeGroupName=NodeGroupName,
        NumCores=NumCores,
        NumNodes=NumNodes,
        NumProcesses=NumProcesses,
        EnableMpi=EnableMpi,
        Environment=Environment,
        SingleNode=SingleNode,
        Exclusive=Exclusive
    )


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
        simulation.add_asset(Asset(filename=file_name, content=ctn))

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


def add_schedule_config(
    item: Union[Experiment, Simulation, TemplatedSimulations],
    command: str = None,
    NodeGroupName: Optional[str] = None,    # COMPS MSHPC or COMPS Slurm
    NumCores: Optional[int] = None,         # COMPS MSHPC or COMPS Slurm
    NumNodes: Optional[int] = None,         # COMPS Slurm only
    NumProcesses: Optional[int] = None,     # COMPS Slurm only
    EnableMpi: Optional[bool] = None,       # COMPS Slurm only
    Environment: Optional[dict] = None,     # COMPS Slurm only
    SingleNode: Optional[bool] = None,      # COMPS MSHPC only
    Exclusive: Optional[bool] = None        # COMPS MSHPC only
):
    """
    Add scheduling config to an Item.

    Scheduling config supports adding to Experiments, Simulations, and TemplatedSimulations

    Args:
        item: Item to add scheduling config to
        command: Command to run
        NodeGroupName: The cluster node-group to commission to (COMPS MSHPC and COMPS Slurm)
        NumCores: The number of cores to reserve (COMPS MSHPC and COMPS Slurm)
        NumNodes: The number of nodes to schedule (COMPS Slurm only)
        NumProcesses: The number of processes to execute (COMPS Slurm only)
        EnableMpi: Whether to run the job with mpiexec (COMPS Slurm only)
        Environment: Environment variables to set in the job environment (COMPS Slurm only)
        Exclusive: Whether nodes should be exclusively allocated to this job (COMPS MSHPC only)
        SingleNode: Limit all reserved cores to the same compute node (COMPS MSHPC only)

    Returns:
        None

    Ref: https://github.com/InstituteforDiseaseModeling/COMPS-Postman-Tests/blob/master/Slurm-conf.csv
         https://github.com/InstituteforDiseaseModeling/COMPS-Postman-Tests/blob/master/mshpc-conf.csv
    """
    config = dict(Command=command)
    config.update({k: v for k, v in {
        'NodeGroupName': NodeGroupName,
        'NumCores': NumCores,
        'NumNodes': NumNodes,
        'NumProcesses': NumProcesses,
        'EnableMpi': EnableMpi,
        'Environment': Environment,
        'SingleNode': SingleNode,
        'Exclusive': Exclusive,
    }.items() if v is not None})  # only include params that were explicitly passed
    _add_work_order_asset(item, config, file_name="WorkOrder.json")
