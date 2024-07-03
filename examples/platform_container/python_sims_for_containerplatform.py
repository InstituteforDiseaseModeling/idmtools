# Here's a simple Python example that runs inside a local Docker container using the idmtools_platform_container package.

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

from idmtools_test import COMMON_INPUT_PATH

# job dir is where the experiment will be run.
# job_directory = os.path.join(os.path.expanduser('~'), "example")
# Define Container Platform. For full list of parameters see container_platform.py in idmtools_platform_container
platform = Platform('CONTAINER', job_directory="DEST")

#Define our base task. Normally, you want to do set any assets/configurations you want across the
# all the different Simulations we are going to build for our experiment. Here we set c to 0 since we do not want to
# sweep it
task = JSONConfiguredPythonTask(script_path=os.path.join("..", "python_model", "inputs", "python", "Assets", "model.py"),
                                parameters=(dict(c=0)))
task.python_path = "python3"

# now let's use this task to create a TemplatedSimulation builder. This will build new simulations from sweep builders
# we will define later. We can also use it to manipulate the base_task or the base_simulation
ts = TemplatedSimulations(base_task=task)
# We can define common metadata like tags across all the simulations using the base_simulation object
ts.base_simulation.tags['tag1'] = 1

# Since we have our templated simulation object now, let's define our sweeps
# To do that we need to use a builder
builder = SimulationBuilder()

# Define an utility function that will update a single parameter at a
# # time on the model and add that param/value pair as a tag on our simulation.
def param_update(simulation: Simulation, param: str, value: Any) -> Dict[str, Any]:
    """
    This function is called during sweeping allowing us to pass the generated sweep values to our Task Configuration.

    We always receive a Simulation object. We know that simulations all have tasks and that for our particular set
    of simulations they will all include JSONConfiguredPythonTask. We configure the model with calls to set_parameter
    to update the config. In addition, we can return a dictionary of tags to add to the simulations so we return
    the output of the 'set_parameter' call since it returns the param/value pair we set

    Args:
        simulation: Simulation we are configuring
        param: Param string passed to use
        value: Value to set param to

    Returns:

    """
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
experiment.assets.add_directory(assets_directory=os.path.join("..", "python_model", "inputs", "python", "Assets"))

# Create suite
suite = Suite(name='Idm Suite')
suite.update_tags({'name': 'suite_tag', 'idmtools': '123'})
# Add experiment to the suite
suite.add_experiment(experiment)

suite.run(platform=platform, wait_until_done=True)
# run following command to check status
print("idmtools file DEST status --exp-id " + experiment.id)
sys.exit(0 if experiment.succeeded else -1)



