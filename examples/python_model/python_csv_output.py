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

from idmtools.builders import ExperimentBuilder
from idmtools.core.platform_factory import Platform
from idmtools.managers import ExperimentManager

from idmtools_models.python.python_experiment import PythonExperiment


# Update and set simulation configuration parameters
def param_update(simulation, param, value):
    return simulation.set_parameter(param, value)


setA = partial(param_update, param="a")

class setParam:
    def __init__(self, param):
        self.param = param

    def __call__(self, simulation, value):
        return param_update(simulation, self.param, value)


# Now create an experiment using PythonExperiment. This type of experiment takes:
# name: The name of the experiment
# model_path: The path to the python file containing the model
# For this example, we will use the model defined in inputs/python_model_with_deps/model.py.
experiment = PythonExperiment(name=os.path.split(sys.argv[0])[1],
                              model_path=os.path.join("inputs", "csv_inputs", "Assets", "model.py"))
experiment.tags["tag1"] = 1

experiment.base_simulation.set_parameter("c", 0)
experiment.assets.add_directory(assets_directory=os.path.join("inputs", "csv_inputs", "Assets"))

# Now that the experiment is created, we can add sweeps to it
builder = ExperimentBuilder()
builder.add_sweep_definition(setA, range(3))
builder.add_sweep_definition(setParam("b"), [1, 2, 3])

experiment.add_builder(builder)

# In order to run the experiment, we need to create a `Platform` and an `ExperimentManager`.
# The `Platform` defines where we want to run our simulation.
# You can easily switch platforms by changing the Platform to for example 'Local'
platform = Platform('COMPS2')

em = ExperimentManager(experiment=experiment, platform=platform)
# The last step is to call run() on the ExperimentManager to run the simulations.
em.run()
