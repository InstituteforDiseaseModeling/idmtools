"""
idmtools utility.

Copyright 2025, Gates Foundation. All rights reserved.
"""
import numpy as np
from typing import Dict, Any, List
from idmtools.entities.simulation import Simulation
from logging import getLogger, DEBUG

logger = getLogger()


##################################################
# Sweeping utility functions
##################################################
def set_param(simulation: Simulation, param: str, value: Any) -> Dict[str, Any]:
    """
    Set a specific parameter value on the simulation task config.

    Args:
        simulation (Simulation): idmtools Simulation object.
        param (str): Name of the parameter to modify.
        value (Any): New value to set.

    Returns:
        Dict[str, Any]: A dictionary containing the parameter name and value.
    """
    try:
        return simulation.task.set_parameter(param, value)
    except ValueError:
        if "parameters" in simulation.task.config:
            config = simulation.task.config.parameters
        else:
            config = simulation.task.config

        config[param] = value
        return {param: value}


def sweep_functions(simulation: Simulation, func_list: List) -> Dict[str, Any]:
    """
    Apply a list of sweep functions to a simulation.

    Args:
        simulation (Simulation): The simulation to update.
        func_list (List[Callable]): List of functions that apply sweeps to the simulation.

    Returns:
        Dict[str, Any]: A dictionary of aggregated metadata from each sweep function.
    """
    tags_updated = {}
    for func in func_list:
        tags = func(simulation)
        if tags:
            tags_updated.update(tags)
    return tags_updated


class ItvFn:
    """
    Sweeping utility for modifying interventions (campaign layer) during sweeps.

    Requirements:
        - func must accept an emod-api campaign object as its first argument.
        - func must return a dictionary of metadata (i.e: tags).

    Returns:
        Dict[str, Any]: Metadata returned by the intervention function, with numpy types cast to Python types.
    """
    def __init__(self, func, *args, **kwargs):  # noqa: D107
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def __call__(self, simulation: Simulation):  # noqa: D102
        import emod_api.campaign as campaign
        campaign.reset()

        matadata = self.func(campaign, *self.args, **self.kwargs)

        # Add new campaign events
        events = campaign.campaign_dict["Events"]
        simulation.task.campaign.add_events(events)

        # Handle adhoc (custom) individual events
        adhoc_events = campaign.get_adhocs()
        if len(adhoc_events) > 0:
            if logger.isEnabledFor(DEBUG):
                logger.debug("Found adhoc events in campaign. Needs some special processing behind the scenes.")
            if "Custom_Individual_Events" in simulation.task.config.parameters:
                ev_exist = set(simulation.task.config.parameters.Custom_Individual_Events)
                ev_addhoc = set(adhoc_events.keys())
                simulation.task.config.parameters.Custom_Individual_Events = list(ev_exist.union(ev_addhoc))
            else:
                simulation.task.config.parameters.Report_Event_Recorder_Events.extend(list(set(adhoc_events.keys())))

        # Convert numpy types
        if matadata:
            for k, v in matadata.items():
                if isinstance(v, (np.int64, np.float64, np.float32, np.uint32, np.int16, np.int32)):
                    matadata[k] = v.item()

        return matadata


class CfgFn:
    """
    Sweeping utility for modifying simulation configuration parameters.

    Requirements:
        - func must accept simulation.task.config as the first parameter.
        - func must return a dictionary for tagging.

    Returns:
        Dict[str, Any]: Metadata dictionary with Python-native types.
    """

    def __init__(self, func, *args, **kwargs):  # noqa: D107
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def __call__(self, simulation: Simulation):  # noqa: D102
        matadata = self.func(simulation.task.config, *self.args, **self.kwargs)

        # Make sure we cast numpy types into normal system types
        if matadata:
            for k, v in matadata.items():
                if isinstance(v, (np.int64, np.float64, np.float32, np.uint32, np.int16, np.int32)):
                    matadata[k] = v.item()

        return matadata


class SwpFn:
    """
    Sweeping utility for modifying task-level elements (e.g., reports, demographics, climate).

    Requirements:
        - func must accept simulation.task as the first parameter.
        - func must return a metadata dictionary (tags).

    Returns:
        Dict[str, Any]: Metadata with numpy types cast to Python-native types.
    """

    def __init__(self, func, *args, **kwargs):  # noqa: D107
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def __call__(self, simulation: Simulation):  # noqa: D102
        matadata = self.func(simulation.task, *self.args, **self.kwargs)

        # Make sure we cast numpy types into normal system types
        if matadata:
            for k, v in matadata.items():
                if isinstance(v, (np.int64, np.float64, np.float32, np.uint32, np.int16, np.int32)):
                    matadata[k] = v.item()

        return matadata
