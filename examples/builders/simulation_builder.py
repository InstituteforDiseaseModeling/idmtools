import os
import sys

from idmtools.assets import AssetCollection
from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import platform
from idmtools.entities.experiment import Experiment
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_test import COMMON_INPUT_PATH

with platform('Calculon'):
    base_task = JSONConfiguredPythonTask(
        script_path=os.path.join(COMMON_INPUT_PATH, "compsplatform", "working_model.py"),
        # add common assets from existing collection
        common_assets=AssetCollection.from_id('41c1b14d-0a04-eb11-a2c7-c4346bcb1553', as_copy=True)
    )

    ts = TemplatedSimulations(base_task=base_task)
    # sweep parameter
    builder = SimulationBuilder()
    builder.add_sweep_definition(JSONConfiguredPythonTask.set_parameter_partial("min_x"), range(-2, 0))
    builder.add_sweep_definition(JSONConfiguredPythonTask.set_parameter_partial("max_x"), range(1, 3))
    ts.add_builder(builder)

    e = Experiment.from_template(ts, name=os.path.split(sys.argv[0])[1])
    e.run(wait_until_done=True)
    # use system status as the exit code
    sys.exit(0 if e.succeeded else -1)
