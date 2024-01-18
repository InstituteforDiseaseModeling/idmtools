# Example Python Experiment
# In this example, we will demonstrate how to run a python experiment.

# First, import some necessary system and idmtools packages.
# - TemplatedSimulations: To create simulation from a template
# - ExperimentManager: To manage our experiment
# - platform: To specify the platform you want to run your experiment on as a context object
# - JSONConfiguredPythonTask: We want to run an experiment executing a Python script that uses a JSON configuration file
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
# You can easily switch platforms by changing the Platform to for example 'CALCULON'
with platform('BELEGOST'):
    # define our base task as a python model with json config
    base_task = JSONConfiguredPythonTask(
        script_path=os.path.join("inputs", "python", "Assets", "model.py"),
        # set the default parameters to 0
        parameters=(dict(c=0)),
        # add some experiment level assets
        common_assets=AssetCollection.from_directory(os.path.join("inputs", "python", "Assets"))
    )

    # create a templating object using the base task
    ts = TemplatedSimulations(base_task=base_task)
    # Define the parameters we are going to want to sweep
    builder = SimulationBuilder()
    # define two partial callbacks so we can use the built in sweep callback function on the model
    # Since we want to sweep per parameter, and we want need to define a partial for each parameter
    # The JSON model provides utility function for this puprose
    builder.add_sweep_definition(JSONConfiguredPythonTask.set_parameter_partial("a"), range(3))
    builder.add_sweep_definition(JSONConfiguredPythonTask.set_parameter_partial("b"), [1, 2, 3])
    # add the builder to our template
    ts.add_builder(builder)

    # now build experiment
    e = Experiment.from_template(
        ts,
        name=os.path.split(sys.argv[0])[1],
        tags=dict(tag1=1))

    # now we can run the experiment
    e.run(wait_until_done=True)
    # use system status as the exit code
    sys.exit(0 if e.succeeded else -1)
