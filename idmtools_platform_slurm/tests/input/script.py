
import os
import sys
from functools import partial
from typing import Any, Dict

from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities import Suite
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask

from idmtools_test import COMMON_INPUT_PATH


#print(sys.argv[1:])
parms = [int(x) for x in sys.argv[1:]]
job_directory = os.path.join(os.path.expanduser('~'), "DEST")
platform = Platform('SLURM_LOCAL', job_directory=job_directory)

task = JSONConfiguredPythonTask(script_path=os.path.join(COMMON_INPUT_PATH, "python", "model3.py"),
                                envelope="parameters", parameters=(dict(c=0)))
task.python_path = "python3"
ts = TemplatedSimulations(base_task=task)
builder = SimulationBuilder()


def param_update(simulation: Simulation, param: str, value: Any) -> Dict[str, Any]:
    return simulation.task.set_parameter(param, value)

# Let's sweep the parameter 'a'
builder.add_sweep_definition(partial(param_update, param="a"), [parms[0]])

# Let's sweep the parameter 'b'
builder.add_sweep_definition(partial(param_update, param="b"), parms[1:])
ts.add_builder(builder)

experiment = Experiment.from_template(ts, name="slurmjob example")
experiment.assets.add_directory(assets_directory=os.path.join(COMMON_INPUT_PATH, "python", "Assets"))

# Create suite
suite = Suite(name='Idm Suite')
suite.add_experiment(experiment)

suite.run(platform=platform, wait_until_done=True, max_running_jobs=10)


