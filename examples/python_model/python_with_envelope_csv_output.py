# Example Python Experiment
# In this example, we will demonstrate how to run a python experiment.

# First, import some necessary system and idmtools packages.
# - SimulationBuilder: To create sweeps
# - TemplatedSimulations: To create simulations from our templated task and builder
# - Platform: To specify the platform you want to run your experiment on
# - JSONConfiguredPythonTask: We want to run an experiment executing a Python script with a json config
import os
import sys
from idmtools.assets import AssetCollection
from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import platform
from idmtools.entities.experiment import Experiment
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask

# In order to run the experiment, we need to create a `Platform` and an `ExperimentManager`.
# The `Platform` defines where we want to run our simulation.
# You can easily switch platforms by changing the Platform to for example 'Local'
with platform('COMPS2'):
    base_task = JSONConfiguredPythonTask(
        script_path=os.path.join("inputs", "csv_inputs", "Assets", "model1.py"),
        # set default parameters
        parameters=dict(c=0),
        # set a parameter envelope
        envelope="parameters",
        # add some experiment level assets
        common_assets=AssetCollection.from_directory(os.path.join("inputs", "csv_inputs"))
    )

    ts = TemplatedSimulations(base_task=base_task)

    # define our sweeps
    builder = SimulationBuilder()
    builder.add_sweep_definition(JSONConfiguredPythonTask.set_parameter_partial("a"), range(3))
    builder.add_sweep_definition(JSONConfiguredPythonTask.set_parameter_partial("b"), [1, 2, 3])

    ts.add_builder(builder)

    e = Experiment.from_template(ts, name=os.path.split(sys.argv[0])[1], tags=dict(tag1=1))

    e.run(wait_until_done=True)
    # use system status as the exit code
    sys.exit(0 if e.succeeded else -1)
