import os

from idmtools.builders import SimulationBuilder
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.entities.templated_simulation import TemplatedSimulations

from idmtools_models.python.json_python_task import JSONConfiguredPythonTask

# load up an existing experiment with completed simulations
experiment_id = 'c190ced7-00d1-ea11-a2c0-f0921c167862'
platform = Platform('COMPS2')
experiment = platform.get_item(item_id=experiment_id, item_type=ItemType.EXPERIMENT)

# create a new sweep for new simulations
builder = SimulationBuilder()
value = 100
builder.add_sweep_definition(JSONConfiguredPythonTask.set_parameter_partial("a"),
                             [i * i for i in range(value, value+5, 3)])
value = 10
builder.add_sweep_definition(JSONConfiguredPythonTask.set_parameter_partial("b"),
                             [i * i for i in range(value, value+5, 3)])

# Add new simulations to the experiment
model_path = os.path.join("inputs", "python_model_with_deps", "Assets", "newmodel2.py")
sims_template = TemplatedSimulations(base_task=JSONConfiguredPythonTask(script_path=model_path))
sims_template.add_builder(builder=builder)
experiment.add_new_simulations(simulations=sims_template)

# More than one batch of simulations can be added to the experiment before running again
model_path = os.path.join("inputs", "python_model_with_deps", "Assets", "newmodel3.py")
sims_template = TemplatedSimulations(base_task=JSONConfiguredPythonTask(script_path=model_path))
sims_template.add_builder(builder=builder)
experiment.add_new_simulations(simulations=sims_template)

# run all simulations in the experiment that have not run before and wait
platform.run_items(experiment)
platform.wait_till_done(experiment)
