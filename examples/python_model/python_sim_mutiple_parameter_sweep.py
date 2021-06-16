import os
import sys

from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask


def update_command_task(simulation, a, b):
    simulation.task.set_parameter("a", a)
    simulation.task.set_parameter("b", b)
    return {"a": a, "b": b}

task = JSONConfiguredPythonTask(script_path=os.path.join("inputs", "python_model_with_deps", "Assets", "model.py"),
                                parameters=(dict(c=0)))

# now let's use this task to create a TemplatedSimulation builder. This will build new simulations from sweep builders
# we will define later. We can also use it to manipulate the base_task or the base_simulation
ts = TemplatedSimulations(base_task=task)
# We can define common metadata like tags across all the simulations using the base_simulation object
ts.base_simulation.tags['tag1'] = 1

# Since we have our templated simulation object now, let's define our sweeps
# To do that we need to use a builder
builder = SimulationBuilder()
# Now add our sweep on a list
# use following function to sweep multiple parameters at one call
builder.add_multiple_parameter_sweep_definition(update_command_task, range(3), [1, 2, 3])
# or builder.add_multiple_parameter_sweep_definition(update_command_task, a=range(3), b=[1, 2, 3])
# or builder.add_multiple_parameter_sweep_definition(update_command_task, dict(a=range(3), b=[1, 2, 3]))
# or builder.add_multiple_parameter_sweep_definition(update_command_task, **dict(a=range(3), b=[1, 2, 3]))
ts.add_builder(builder)

# Now we can create our Experiment using our template builder
experiment = Experiment.from_template(ts, name=os.path.split(sys.argv[0])[1])
# Add our own custom tag to simulation
experiment.tags["tag1"] = 1
# And maybe some custom Experiment Level Assets
experiment.assets.add_directory(assets_directory=os.path.join("inputs", "python_model_with_deps", "Assets"))

# In order to run the experiment, we need to create a `Platform`
# The `Platform` defines where we want to run our simulation.
# You can easily switch platforms by changing the Platform to for example 'Local'
with Platform('CALCULON'):

    # The last step is to call run() on the ExperimentManager to run the simulations.
    experiment.run(True)
    # use system status as the exit code
    sys.exit(0 if experiment.succeeded else -1)
