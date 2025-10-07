import os
from functools import partial
from typing import Any, Dict

from idmtools.builders import SimulationBuilder
from idmtools.entities import Suite
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask


def create_experiment():

    builder = SimulationBuilder()

    # Sweep parameter "a"
    def param_update(simulation: Simulation, param: str, value: Any) -> Dict[str, Any]:
        return simulation.task.set_parameter(param, value)

    builder.add_sweep_definition(partial(param_update, param="a"), range(3))
    builder.add_sweep_definition(partial(param_update, param="b"), range(5))

    task = JSONConfiguredPythonTask(script_path=os.path.join("inputs", "model3.py"),
                                    envelope="parameters", parameters=(dict(c=0)))
    task.python_path = "python3"
    tags = {"string_tag": "test", "number_tag": 123}
    ts = TemplatedSimulations(base_task=task)
    ts.add_builder(builder)
    suite = Suite()
    suite.tags = {"suite_tag": "suite_tag_value"}
    experiment = Experiment.from_template(ts, name="experiment_test", tags=tags)
    experiment.assets.add_directory(assets_directory=os.path.join("inputs", "Assets"))
    suite.add_experiment(experiment)
    experiment.run(wait_until_done=True)
    return experiment
