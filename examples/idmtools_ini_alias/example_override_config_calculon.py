# Example shows how to override Platform config values without idmtools.ini file in the path
# Note, this example does not use idmtools.ini file. you are free to remove idmtools.ini file and try run this example

import math
import os
import sys
from functools import partial
import numpy as np

from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask


def sample_point_fn(simulation, param, value):
    tags = {}
    # Setup some baseline parameters, but allow them to be overwritten afterwards by inputs to this function
    if param.startswith('META'):
        tags = meta_parameter_handler(simulation.task, param, value)
    else:
        simulation.task.set_parameter(param, value)
        tags[param] = value
    return tags


def meta_parameter_handler(task, param, value):
    tags = {}

    if param == 'META_Overlay':
        task.set_parameter('META_Overlay', value)
        tags[param] = value

    elif param == 'META_Mean_CoeffVar':
        task.set_parameter('Base_Mu', math.log(value[0]) - 1 / 2 * math.log(1 + value[1] ** 2))
        task.set_parameter('Base_Sigma', math.sqrt(math.log(1 + value[1] ** 2)))

        tags['Base_Mean'] = value[0]
        tags['Base_CoeffVar'] = value[1]
        tags[param] = value
    return tags


INPUT_PATH = os.path.join("..", "python_model", "inputs", "python_model_with_deps", "Assets")
task = JSONConfiguredPythonTask(script_path=os.path.join(INPUT_PATH, "model1.py"),
                                parameters={"a": 1, "b": "b_value"})

# now let's use this task to create a TemplatedSimulation builder. This will build new simulations from sweep builders
# we will define later. We can also use it to manipulate the base_task or the base_simulation
ts = TemplatedSimulations(base_task=task)
# We can define common metadata like tags across all the simulations using the base_simulation object
ts.base_simulation.tags['sim_tag'] = 123

builder = SimulationBuilder()

# now add the sweep to our builder
builder.add_sweep_definition(partial(sample_point_fn, param='META_Overlay'),
                             [f'{v:.2e}'.replace('.', 'p') for v in list(np.logspace(-6, -4, 2))])
builder.add_sweep_definition(partial(sample_point_fn, param='META_Mean_CoeffVar'),
                             [(10 * v / 32, 1.0) for v in [2, 4, 7]])

builder.add_sweep_definition(partial(sample_point_fn, param='Run_Number'), [v for v in range(1, 3)])
ts.add_builder(builder)

# Now we can create our Experiment using our template builder
experiment = Experiment.from_template(ts, name=os.path.split(sys.argv[0])[1])
# Add our own custom tag to simulation
experiment.tags["my_tag"] = "test"
# And maybe some custom Experiment Level Assets
experiment.assets.add_directory(assets_directory=INPUT_PATH)

# We can use code to define Platform configuration. "Calculon" is Production linux environment
# To see list of environment aliases, you can run cli command: idmtools info plugins platform-aliases
with Platform('Calculon', priority='Highest', node_group="idm_abcd", num_cores=1):
    # The last step is to call run() on the ExperimentManager to run the simulations.
    experiment.run(True)
    # use system status as the exit code
    sys.exit(0 if experiment.succeeded else -1)
