import os
from typing import Dict

from idmtools.builders import SimulationBuilder
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.entities.simulation import Simulation
from idmtools.entities.templated_simulation import TemplatedSimulations

from idmtools_models.python.json_python_task import JSONConfiguredPythonTask

# load up an existing experiment with completed simulations
experiment_id = 'c37c274a-f790-ea11-a2bf-f0921c167862'
platform = Platform('COMPS2')
experiment = platform.get_item(item_id=experiment_id, item_type=ItemType.EXPERIMENT)

# create a new sweep for new simulations
builder = SimulationBuilder()
value = 100
builder.add_sweep_definition(JSONConfiguredPythonTask.set_parameter_partial("a"),
                             [i * i for i in range(value, value+10, 3)])
builder.add_sweep_definition(JSONConfiguredPythonTask.set_parameter_partial("b"),
                             [i * i for i in range(10, 20, 3)])

model_path = os.path.join("inputs", "python_model_with_deps", "Assets", "model.py")
sims_template = TemplatedSimulations(base_task=JSONConfiguredPythonTask(script_path=model_path))
sims_template.add_builder(builder=builder)

# add new simulations to the experiment, run (only the new simulations), and wait
experiment.add_new_simulations(simulations=sims_template)

platform.run_items(experiment)
platform.wait_till_done(experiment)
