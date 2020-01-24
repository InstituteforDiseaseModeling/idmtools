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
from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.managers import ExperimentManager
from idmtools_models.python.python_experiment import PythonExperiment


# Update and set simulation configuration parameters
def param_update(simulation, param, value):
    return simulation.set_parameter(param, 'sweepR04_a_' + str(value) + '.json')


# Now create an experiment using PythonExperiment. This type of experiment takes:
# name: The name of the experiment
# model_path: The path to the python file containing the model
# For this example, we will use the model defined in inputs/allee_python_model/model.py.
pe = PythonExperiment(name=os.path.split(sys.argv[0])[1],
                      model_path=os.path.join("inputs", "allee_python_model", "run_emod_sweep.py"))
pe.base_simulation.envelope = "parameters"
# pe.retrieve_python_dependencies()

# Example of how to add tags to the Experiment
pe.tags["tag1"] = "example from allee python model with idmtools"

# Add your assets from a file directory to your Experiment
pe.assets.add_directory(assets_directory=os.path.join("inputs", "allee_python_model"))

setA = partial(param_update, param="infile")


class setParam:
    def __init__(self, param):
        self.param = param

    def __call__(self, simulation, value):
        return param_update(simulation, self.param, value)

# Now that the experiment is created, we can add sweeps to it and set additional params
builder = SimulationBuilder()
builder.add_sweep_definition(setA, range(7850, 7855))
pe.base_simulation.set_parameter("fname", "runNsim100.json")
pe.base_simulation.set_parameter("customGrid", 1)
pe.base_simulation.set_parameter("nsims", 100)

pe.builder = builder

# In order to run the experiment, we need to create a `Platform` and an `ExperimentManager`.
# The `Platform` defines where we want to run our simulation.
# You can easily switch platforms by changing the Platform to for example 'Local'
# platform = Platform('Local')
platform = Platform('COMPS2')

em = ExperimentManager(experiment=pe, platform=platform)
# The last step is to call run() on the ExperimentManager to run the simulations.
em.run()
