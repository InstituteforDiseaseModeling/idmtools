import json
from os import PathLike
from typing import List, Union
from idmtools.assets import Asset
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools.entities.templated_simulation import TemplatedSimulations
from logging import DEBUG
import logging

logger = logging.getLogger(__name__)


# utility function to add updated WorkOrder.json to each simulation as linked file via simulation task
# first loads original workorder file from local, then update Command field in it from each simulation object's
# simulation.task.command.cmd, then write updated command to WorkOrder.json, and load this file to simulation
def default_add_workerorder_sweep_callback(simulation, file_name, file_path):
    add_work_order(simulation, file_name=file_name, file_path=file_path)


def _add_work_order_asset(_simulation: Simulation, _file_name: str = "WorkOrder.json",
                          _file_path: Union[str, PathLike] = "./WorkOrder.json", _update: bool = True):

    with open(str(_file_path), "r") as jsonFile:
        data = json.loads(jsonFile.read())

    if _update:
        data["Command"] = _simulation.task.command.cmd

    _simulation.task.transient_assets.add_asset(Asset(filename=_file_name, content=json.dumps(data)))

    setattr(_simulation, 'scheduling', True)


def add_work_order(item: Union[Experiment, Simulation, TemplatedSimulations], file_name: str = "WorkOrder.json",
                   file_path: Union[str, PathLike] = "./WorkOrder.json"):
    if isinstance(item, Simulation):
        _add_work_order_asset(item, _file_name=file_name, _file_path=file_path, _update=True)
    elif isinstance(item, TemplatedSimulations):
        _add_work_order_asset(item.base_simulation, _file_name=file_name, _file_path=file_path, _update=False)
    elif isinstance(item, Experiment):
        if isinstance(item.simulations.items, TemplatedSimulations):
            if len(item.simulations.items) == 0:
                raise ValueError("You cannot run an empty experiment")
            if logger.isEnabledFor(DEBUG):
                logger.debug("Using Base task from template for WorkOrder.json assets")
            _add_work_order_asset(item.simulations.items.base_simulation, _file_name=file_name, _file_path=file_path,
                                  _update=False)
            for sim in item.simulations.items.extra_simulations():
                _add_work_order_asset(sim, _file_name=file_name, _file_path=file_path, _update=True)
        elif isinstance(item.simulations.items, List):
            if len(item.simulations.items) == 0:
                raise ValueError("You cannot run an empty experiment")
            if logger.isEnabledFor(DEBUG):
                logger.debug("Using all tasks to gather assets")
            for sim in item.simulations.items:
                _add_work_order_asset(sim, _file_name=file_name, _file_path=file_path, _update=True)
        elif isinstance(item.simulations.items, List) and len(item.simulations.items) == 0:
            raise ValueError("You cannot run an empty experiment")
    else:
        raise ValueError("The method only support object type: Experiment, Simulation, TemplatedSimulations!")


def _add_schedule_config_asset(simulation: Simulation, _config: dict, _update: bool = True):
    if _update:
        _config["Command"] = simulation.task.command.cmd

    ctn = json.dumps(_config, indent=3)
    simulation.task.transient_assets.add_asset(Asset(filename="Work_order.json", content=ctn))


def add_schedule_config(item: Union[Experiment, Simulation, TemplatedSimulations], command: str = None,
                        node_group_name: str = 'idm_cd', num_cores: int = 1, **config_opts):
    config = dict(Command=command, NodeGroupName=node_group_name, NumCores=num_cores)
    config.update(config_opts)

    if isinstance(item, Simulation):
        _add_schedule_config_asset(item, _config=config, _update=True)
    elif isinstance(item, TemplatedSimulations):
        _add_schedule_config_asset(item.base_simulation, _config=config, _update=False)
    elif isinstance(item, Experiment):
        if isinstance(item.simulations.items, TemplatedSimulations):
            if len(item.simulations.items) == 0:
                raise ValueError("You cannot run an empty experiment")
            if logger.isEnabledFor(DEBUG):
                logger.debug("Using Base task from template for WorkOrder.json assets")
            _add_schedule_config_asset(item.simulations.items.base_simulation, _config=config, _update=False)
            for sim in item.simulations.items.extra_simulations():
                _add_schedule_config_asset(sim, _config=config, _update=True)
        elif isinstance(item.simulations.items, List):
            if len(item.simulations.items) == 0:
                raise ValueError("You cannot run an empty experiment")
            if logger.isEnabledFor(DEBUG):
                logger.debug("Using all tasks to gather assets")
            for sim in item.simulations.items:
                _add_schedule_config_asset(sim, _config=config, _update=True)
        elif isinstance(item.simulations.items, List) and len(item.simulations.items) == 0:
            raise ValueError("You cannot run an empty experiment")
    else:
        raise ValueError("The method only support object type: Experiment, Simulation, TemplatedSimulations!")


