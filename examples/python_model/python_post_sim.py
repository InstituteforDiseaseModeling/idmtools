# Example Python Experiment with JSON Configuration
# In this example, we will demonstrate how to add simulation post hood

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


def sim_post_hook(simulation):
    """
    This function is called after simulation created but before commission
    Here provide user a chance to get real simulation id. As an example, here
    we output simulation as a file.

    Args:
        simulation: Simulation we are configuring

    Returns:

    """
    from COMPS.Data.SimulationFile import SimulationFile
    comps_sim = simulation.get_platform_object()
    comps_sim.add_file(simulationfile=SimulationFile('sim_id.txt', 'input'), data=bytes(str(comps_sim.id), 'utf-8'))
    comps_sim.save()


# first let's define our base task. Normally, you want to do set any assets/configurations you want across the
# all the different Simulations we are going to build for our experiment. Here we set c to 0 since we do not want to
# sweep it
task = JSONConfiguredPythonTask(script_path=os.path.join("inputs", "python_model_with_deps", "Assets", "model.py"),
                                parameters=(dict(c=0)))

# add function to be called after each simulation creation
task.add_post_sim_creation_hook(sim_post_hook)

# now let's use this task to create a TemplatedSimulation builder. This will build new simulations from sweep builders
# we will define later. We can also use it to manipulate the base_task or the base_simulation
ts = TemplatedSimulations(base_task=task)
# We can define common metadata like tags across all the simulations using the base_simulation object
ts.base_simulation.tags['tag1'] = 1

# Since we have our templated simulation object now, let's define our sweeps
# To do that we need to use a builder
builder = SimulationBuilder()


def param_update(simulation: Simulation, param: str, value: Any) -> Dict[str, Any]:
    return simulation.task.set_parameter(param, value)


# Let's sweep the parameter 'a' for the values 0-2. Since our utility function requires a Simulation, param, and value
# but the sweep framework all calls our function with Simulation, value, let's use the partial function to define
# that we want the param value to always be "a" so we can perform our sweep
setA = partial(param_update, param="a")
# now add the sweep to our builder
builder.add_sweep_definition(setA, range(3))

ts.add_builder(builder)

# Now we can create our Experiment using our template builder
experiment = Experiment.from_template(ts, name=os.path.split(sys.argv[0])[1])
# Add our own custom tag to simulation
experiment.tags["tag1"] = 1
# And maybe some custom Experiment Level Assets
experiment.assets.add_directory(assets_directory=os.path.join("inputs", "python_model_with_deps", "Assets"))

with Platform('BELEGOST'):
    # The last step is to call run() on the ExperimentManager to run the simulations.
    experiment.run(True)
    # use system status as the exit code
    sys.exit(0 if experiment.succeeded else -1)
