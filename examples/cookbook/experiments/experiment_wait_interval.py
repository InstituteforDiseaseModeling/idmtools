import os
import sys
from functools import partial

from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask

model_path = os.path.join("..", "..", "python_model", "inputs", "python_model_with_deps", "Assets", "model.py")
task = JSONConfiguredPythonTask(script_path=model_path)

ts = TemplatedSimulations(base_task=task)

builder = SimulationBuilder()
# now add the sweep to our builder
builder.add_sweep_definition(partial(JSONConfiguredPythonTask.set_parameter_sweep_callback, param="a"), range(2))

# add our builder to the templated simulations
ts.add_builder(builder)

# Now we can create our Experiment using our template builder
experiment = Experiment(name=os.path.split(sys.argv[0])[1], simulations=ts)
platform = Platform('CALCULON')
experiment.run()

# customized wait interval to 1 second
platform.wait_till_done(experiment, refresh_interval=1)
# use system status as the exit code
sys.exit(0 if experiment.succeeded else -1)
