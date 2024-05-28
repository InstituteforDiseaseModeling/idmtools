import os
import sys
from functools import partial

from idmtools.assets import AssetCollection
from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import platform
from idmtools.entities.experiment import Experiment
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.comps import get_asset_collection_id_for_simulation_id

# connect to COMPS
with platform('SlurmStage'):
    # get asset collection from an existing sim
    # Use existing simulation id
    sim_id = '7415d267-2df1-ee11-9302-f0921c167864'  # comps sim id
    collection_id = get_asset_collection_id_for_simulation_id(sim_id)

    # define our base task with addition of the Comps Asset collection
    base_task = JSONConfiguredPythonTask(
        script_path=os.path.join(COMMON_INPUT_PATH, "compsplatform", "working_model.py"),
        common_assets=AssetCollection.from_id(collection_id, as_copy=True)
    )

    # create a templated simulation builder using our base task
    ts = TemplatedSimulations(base_task=base_task)
    # sweep parameter
    builder = SimulationBuilder()
    set_min = partial(JSONConfiguredPythonTask.set_parameter_sweep_callback, param="min_x")
    set_max = partial(JSONConfiguredPythonTask.set_parameter_sweep_callback, param="min_x")
    builder.add_sweep_definition(set_min, range(-2, 0))
    builder.add_sweep_definition(set_max, range(1, 3))

    # add the sweep builder to the template
    ts.add_builder(builder)

    # run the experiment and wait
    em = Experiment.from_template(ts, name=os.path.split(sys.argv[0])[1])
    em.run(wait_until_done=True)
    # use system status as the exit code
    sys.exit(0 if em.succeeded else -1)
