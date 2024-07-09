# This example demonstrates how to run a simulation using a container platform with idmtools.ini file.
import os
import sys
from functools import partial
from typing import Any, Dict
from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities import Suite
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask


assets_directory = os.path.join("..", "python_model", "inputs", "python", "Assets")
# The platform is created with the name 'My_container' which is defined in the idmtools.ini file
platform = Platform('My_container')
task = JSONConfiguredPythonTask(script_path=os.path.join(assets_directory, "model.py"), parameters=(dict(c=0)))
task.python_path = "python3"

ts = TemplatedSimulations(base_task=task)
ts.base_simulation.tags['tag1'] = 1
builder = SimulationBuilder()

def param_update(simulation: Simulation, param: str, value: Any) -> Dict[str, Any]:
    return simulation.task.set_parameter(param, value)

# Let's sweep the parameter 'a' for the values 0-2
builder.add_sweep_definition(partial(param_update, param="a"), range(3))

# Let's sweep the parameter 'b' for the values 0-4
builder.add_sweep_definition(partial(param_update, param="b"), range(5))
ts.add_builder(builder)

# Now we can create our Experiment using our template builder
experiment = Experiment.from_template(ts, name="python example")
# Add our own custom tag to experiment
experiment.tags["tag1"] = 1
# And all files from dir at ../python_model/python/Assets folder to experiment folder
experiment.assets.add_directory(assets_directory=assets_directory)

# Create suite
suite = Suite(name='Idm Suite')
suite.update_tags({'name': 'suite_tag', 'idmtools': '123'})
# Add experiment to the suite
suite.add_experiment(experiment)

suite.run(platform=platform, wait_until_done=True)
# run following command to check status
print("idmtools file DEST status --exp-id " + experiment.id)
sys.exit(0 if experiment.succeeded else -1)



