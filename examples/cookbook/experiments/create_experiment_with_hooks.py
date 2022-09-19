import os
import sys
import typing
from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools.utils.entities import save_id_as_file_as_hook
from time import time
if typing.TYPE_CHECKING:
    from idmtools_platform_comps.comps_platform import COMPSPlatform

# Define our base task
task = JSONConfiguredPythonTask(script_path=os.path.join("..", "..", "python_model", "inputs", "python_model_with_deps",
                                                         "Assets", "model.py"), parameters=(dict(c=0)))
ts = TemplatedSimulations(base_task=task)

# Build sweeps for our simulations
builder = SimulationBuilder()

class setParam:
    def __init__(self, param):
        self.param = param

    def __call__(self, simulation, value):
        return simulation.task.set_parameter(self.param, value)


builder.add_sweep_definition(setParam("a"), [1, 2, 3])
builder.add_sweep_definition(setParam("b"), [1, 2])

ts.add_builder(builder)

# Create our experiment
experiment = Experiment.from_template(ts, name=os.path.split(sys.argv[0])[1])

# Add our pre-creation and post-creation hooks:
#   Our pre-creation hook adds the date as a tag to our experiment
#   Our post-creation hook saves the experiment ID within a file titled '{item.item_type}.{item.name}.id' (within current directory)
ran_at = str(time())

def add_date_as_tag(experiment: Experiment, platform: 'COMPSPlatform'):
    experiment.tags['date'] = ran_at

# Add a pre/post creation hook to either an experiment or a work item using the 'add_pre_creation_hook' or 'add_post_creation_hook' methods
experiment.add_pre_creation_hook(add_date_as_tag)
experiment.add_post_creation_hook(save_id_as_file_as_hook)

with Platform('BELEGOST'):
    experiment.run(True)
    sys.exit(0 if experiment.succeeded else -1)