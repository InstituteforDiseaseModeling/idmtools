import os
import sys
from functools import partial
from typing import Any, Dict

from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask

parameters = {'b' + str(x): x**2 for x in (2, 4, 6)}
task = JSONConfiguredPythonTask(script_path=os.path.join("inputs", "python_model_with_deps", "Assets", "model.py"),
                                parameters=parameters)


ts = TemplatedSimulations(base_task=task)
ts.base_simulation.tags['tag1'] = 1


builder = SimulationBuilder()


def param_update(simulation: Simulation, param: str, value: Any) -> Dict[str, Any]:
    return simulation.task.set_parameter(param, value)


setA = partial(param_update, param="a")
# now add the sweep to our builder
builder.add_sweep_definition(setA, range(3))


class setParam:
    def __init__(self, param):
        self.param = param

    def __call__(self, simulation, value):
        return simulation.task.set_parameter(self.param, value)


# Now add our sweep on a list
builder.add_sweep_definition(setParam("b"), [1, 2, 3])
# add our builder to the templated simulations
ts.add_builder(builder)

# Now we can create our Experiment using our template builder
experiment = Experiment(name=os.path.split(sys.argv[0])[1], simulations=ts)
# Add our own custom tag to simulation
experiment.tags["tag1"] = 1
# And maybe some custom Experiment Level Assets
experiment.assets.add_directory(assets_directory=os.path.join("inputs", "python_model_with_deps", "Assets"))

with Platform('CALCULON'):
    experiment.run(wait_until_done=True)
    sys.exit(0 if experiment.succeeded else -1)
