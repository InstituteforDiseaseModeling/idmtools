"""
There are 2 ways to run this example.
Option1: run "python3 example2.py".
- This will run python script (i.e example2.py) on Slurm head node .
- example2.py first build experiment/simulations on head node
- example2.py then triggers a Slurm job to run experiment/simulations

Option2, run "sbatch sbatch_for_example2.sh".
- This will trigger a Slurm job to run example2.py script on computation node.
- example2.py first build experiment/simulations on Computation node
- example2.py then kicks out another slurm job (different jobid) to run experiment/simulations

These two samples takes Northwestern University Slurm environment QUEST as a demonstration and the samples are supposed
 to run on QUEST head nodes. If you want to run these samples on other Slurm environments, based on their Slurm setup
 configuration or requirements, you may have to pass different Slurm parameters (here, partition, time and account are
 required Slurm parameters in QUEST).
"""
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

# job dir should be /home/username/example/slurm_job
job_directory = os.path.join(os.path.expanduser('~'), "example/slurm_job")

# Note, this example only runs on NU with their partition and acct
platform = Platform('SLURM_LOCAL', job_directory=job_directory, partition='b1139', time='10:00:00',
                        account='b1139')

task = JSONConfiguredPythonTask(script_path=os.path.join(COMMON_INPUT_PATH, "python", "model3.py"),
                                envelope="parameters", parameters=(dict(c=0)))
task.python_path = "python3"
ts = TemplatedSimulations(base_task=task)
ts.base_simulation.tags['tag1'] = 1
builder = SimulationBuilder()


def param_update(simulation: Simulation, param: str, value: Any) -> Dict[str, Any]:
    return simulation.task.set_parameter(param, value)

# Let's sweep the parameter 'a' for the values 0-2
builder.add_sweep_definition(partial(param_update, param="a"), range(3))

# Let's sweep the parameter 'b' for the values 0-4
builder.add_sweep_definition(partial(param_update, param="b"), range(5))
ts.add_builder(builder)

experiment = Experiment.from_template(ts, name="python example")
experiment.assets.add_directory(assets_directory=os.path.join(COMMON_INPUT_PATH, "python", "Assets"))

# Create suite
suite = Suite(name='Idm Suite')
suite.add_experiment(experiment)

suite.run(platform=platform, wait_until_done=True, max_running_jobs=10,
          retries=5, dry_run=False)
sys.exit(0 if experiment.succeeded else -1)


