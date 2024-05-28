# Example Python Experiment with JSON Configuration
# In this example, we will demonstrate how to run a python experiment with JSON Configuration

# First, import some necessary system and idmtools packages.
# - TemplatedSimulations: A utility that builds simulations from a template
# - SimulationBuilder: An interface to different types of sweeps. It is used in conjunction with TemplatedSimulations
# - Platform: To specify the platform you want to run your experiment on
# - JSONConfiguredPythonTask: We want to run an task executing a Python script. We will run a task in each simulation
# using this object. This particular task has a json config that is generated as well. There are other python task
# we either different or no configuration formats.
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

# We have python model defined in "model.py" which has 3 parameters: a, b, c and supports
# a json config from a file named "config".json. We want to sweep the parameters a for the values 0-2 and b for the
# values 1-3 and keep c as value 0.
# To accomplish this, we are going to proceed in a few high-level steps. See https://bit.ly/37DHUf0 for workflow
# 1. Define our base task. This task is the common configuration across all our tasks. For us, that means some basic
#    run info like script path as well as our parameter/value we don't plan on sweeping, c
# 2. Then we will define our TemplateSimulations object that will use our task to build a series of simulations
# 3. Then we will define a SimulationBuilder and define our sweeps. This will invlove also writing some callback
# functions that update the each task's config with the swep values
# 4. Then we will add our simulation builder to our TemplateSimulation object.
# 5. We will then build our Experiment object using the TemplateSimulations as our simulations list.
# 6. Lastly we will run the experiment on the platform

# first let's define our base task. Normally, you want to do set any assets/configurations you want across the
# all the different Simulations we are going to build for our experiment. Here we set c to 0 since we do not want to
# sweep it
task = JSONConfiguredPythonTask(script_path=os.path.join("inputs", "python", "Assets", "model.py"),
                                parameters=(dict(c=0)))

# now let's use this task to create a TemplatedSimulation builder. This will build new simulations from sweep builders
# we will define later. We can also use it to manipulate the base_task or the base_simulation
ts = TemplatedSimulations(base_task=task)
# We can define common metadata like tags across all the simulations using the base_simulation object
ts.base_simulation.tags['tag1'] = 1

# Since we have our templated simulation object now, let's define our sweeps
# To do that we need to use a builder
builder = SimulationBuilder()

# When adding sweep definitions, you need to generally provide two items
# See https://bit.ly/314j7xS for a diagram of how the Simulations are built using TemplateSimulations +
# SimulationBuilders
# 1. A callback function that will be called for every value in the sweep. This function will receive a Simulation
#    object and a value. You then define how to use those within the simulation. Generally, you want to pass those
#    to your task's configuration interface. In this example, we are using JSONConfiguredPythonTask which has a
#    set_parameter function that takes a Simulation, a parameter name, and a value. To pass to this function, we will
#    user either a class wrapper or function partials
# 2. A list/generator of values

# Since our models uses a json config let's define an utility function that will update a single parameter at a
# time on the model and add that param/value pair as a tag on our simulation.


def param_update(simulation: Simulation, param: str, value: Any) -> Dict[str, Any]:
    """
    This function is called during sweeping allowing us to pass the generated sweep values to our Task Configuration

    We always receive a Simulation object. We know that simulations all have tasks and that for our particular set
    of simulations they will all include JSONConfiguredPythonTask. We configure the model with calls to set_parameter
    to update the config. In addition, we are can return a dictionary of tags to add to the simulations so we return
    the output of the 'set_parameter' call since it returns the param/value pair we set

    Args:
        simulation: Simulation we are configuring
        param: Param string passed to use
        value: Value to set param to

    Returns:

    """
    return simulation.task.set_parameter(param, value)


# Let's sweep the parameter 'a' for the values 0-2. Since our utility function requires a Simulation, param, and value
# but the sweep framework all calls our function with Simulation, value, let's use the partial function to define
# that we want the param value to always be "a" so we can perform our sweep
setA = partial(param_update, param="a")
# now add the sweep to our builder
builder.add_sweep_definition(setA, range(3))


# An alternative to using partial is define a class that store the param and is callable later. let's use that technique
# to perform a sweep one the values 1-3 on parameter b

# First define our class. The trick here is we overload __call__ so that after we create the class, and calls to the
# instance will be relayed to the task in a fashion identical to the param_update function above. It is generally not
# best practice to define a class like this in the body of our main script so it is advised to place this in a library
# or at the very least the top of your file.
class setParam:
    def __init__(self, param):
        self.param = param

    def __call__(self, simulation, value):
        return simulation.task.set_parameter(self.param, value)


# Now add our sweep on a list
builder.add_sweep_definition(setParam("b"), [1, 2, 3])
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
with Platform(block='COMPS', endpoint = 'https://comps.idmod.org', environment='Calculon', type='COMPS') :

    # The last step is to call run() on the ExperimentManager to run the simulations.
    experiment.run(True)
    # use system status as the exit code
    sys.exit(0 if experiment.succeeded else -1)
