# Example Python Experiment
# In this example, we will demonstrate how to run a python experiment.

# First, import some necessary system and idmtools packages.
# - ExperimentBuilder: To create sweeps
# - ExperimentManager: To manage our experiment
# - Platform: To specify the platform you want to run your experiment on
# - PythonExperiment: We want to run an experiment executing a Python script
import os
import sys
from functools import partial

from idmtools.assets import AssetCollection
from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
# In order to run the experiment, we need to create a `Platform` and an `ExperimentManager`.
# The `Platform` defines where we want to run our simulation.
# You can easily switch platforms by changing the Platform to for example 'CALCULON'
# with Platform('CALCULON'):
from idmtools.entities.experiment import Experiment
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_platform_comps.utils.python_requirements_ac.requirements_to_asset_collection import RequirementsToAssetCollection

platform = Platform('CALCULON')

pl = RequirementsToAssetCollection(platform,
                                   requirements_path=os.path.join("inputs", "allee_python_model", "requirements.txt"))

ac_id = pl.run()
pandas_assets = AssetCollection.from_id(ac_id, as_copy=True)

base_task = JSONConfiguredPythonTask(
    # specify the path to the script. This is most likely a scientific model
    script_path=os.path.join("inputs", "allee_python_model", "run_emod_sweep.py"),
    envelope='parameters',
    parameters=dict(
        fname="runNsim100.json",
        customGrid=1,
        nsims=100
    ),
    common_assets=pandas_assets
)

# Update and set simulation configuration parameters
def param_update(simulation, param, value):
    return simulation.task.set_parameter(param, 'sweepR04_a_' + str(value) + '.json')


setA = partial(param_update, param="infile")

# define our template
ts = TemplatedSimulations(base_task=base_task)
# Now that the experiment is created, we can add sweeps to it and set additional params
builder = SimulationBuilder()
builder.add_sweep_definition(setA, range(7850, 7855))
# add sweep builder to template
ts.add_builder(builder)

# create experiment
e = Experiment.from_template(
    ts,
    name=os.path.split(sys.argv[0])[1],
    assets=AssetCollection.from_directory(os.path.join("inputs", "allee_python_model"))
)

e.run(wait_until_done=True)

# use system status as the exit code
sys.exit(0 if e.succeeded else -1)
