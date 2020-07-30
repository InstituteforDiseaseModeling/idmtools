import os
from typing import Dict

from idmtools.builders import SimulationBuilder
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.entities.simulation import Simulation
from idmtools.entities.templated_simulation import TemplatedSimulations

from idmtools_models.python.json_python_task import JSONConfiguredPythonTask

# load up an existing experiment with completed simulations
experiment_id = 'c190ced7-00d1-ea11-a2c0-f0921c167862'
platform = Platform('COMPS2')
experiment = platform.get_item(item_id=experiment_id, item_type=ItemType.EXPERIMENT)

# # ck4, debug ONLY 7/27, this block
# from idmtools.assets import AssetCollection, Asset
# file = os.path.join("inputs", "python_model_with_deps", "Assets", "priormodelasset.py")
# experiment.assets = AssetCollection(assets=[Asset(absolute_path=file)])

# create a new sweep for new simulations
builder = SimulationBuilder()
value = 100
builder.add_sweep_definition(JSONConfiguredPythonTask.set_parameter_partial("a"),
                             [i * i for i in range(value, value+5, 3)])
builder.add_sweep_definition(JSONConfiguredPythonTask.set_parameter_partial("b"),
                             [i * i for i in range(10, 15, 3)])

model_path = os.path.join("inputs", "python_model_with_deps", "Assets", "newmodel3.py")
sims_template = TemplatedSimulations(base_task=JSONConfiguredPythonTask(script_path=model_path))
sims_template.add_builder(builder=builder)
experiment.add_new_simulations(simulations=sims_template)

# TODO: fix this. Addint a second TemplatedSiulations leads to NOT adding assets for PRIOR TS. (e.g. not uploading newmodel3.py)
# TODO: TASK info seems untouched, e.g. prior block task is still: python newmodel3.py (but only model.py is available; no sim assets)
model_path = os.path.join("inputs", "python_model_with_deps", "Assets", "newmodel2.py")
sims_template = TemplatedSimulations(base_task=JSONConfiguredPythonTask(script_path=model_path))
sims_template.add_builder(builder=builder)
experiment.add_new_simulations(simulations=sims_template)

# # ck4, testing ONLY. remove ASAP, 7/27 TODO
# experiment.add_new_simulations(simulations=[])

# add new simulations to the experiment, run (only the new simulations), and wait

platform.run_items(experiment)
platform.wait_till_done(experiment)
