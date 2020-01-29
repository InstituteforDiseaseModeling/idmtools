from typing import Any, Dict

from idmtools.entities.simulation import Simulation


def update_task_with_set_parameter(simulation: Simulation, param: str, value: Any) -> Dict[str, Any]:
    if not hasattr(simulation.task, 'set_parameter'):
        raise ValueError("update_task_with_set_parameter can only be used on tasks with a set_parameter")
    return simulation.task.set_parameter(param, value)
