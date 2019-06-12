import os
from functools import partial

from idmtools.entities import ExperimentBuilder
from idmtools.managers import ExperimentManager
from idmtools.platforms import COMPSPlatform
from idmtools.platforms import LocalPlatform
from idmtools_models.python.PythonExperiment import PythonExperiment


def param_update(simulation, param, value):
    return simulation.set_parameter(param, 'sweepR04_a_' + str(value) + '.json')


experiment = PythonExperiment(name="Allee python model example", model_path=os.path.join("work", "inputs", "allee_python_model", "run_dtk_sweep.py"))
experiment.tags["tag1"] = "example from allee python model with idmtools"

experiment.assets.add_directory(assets_directory=os.path.join("work", "inputs", "allee_python_model"))

setA = partial(param_update, param="infile")


class setParam:
    def __init__(self, param):
        self.param = param

    def __call__(self, simulation, value):
        return param_update(simulation, self.param, value)


builder = ExperimentBuilder()
builder.add_sweep_definition(setA, range(7850,7855))
experiment.base_simulation.set_parameter("fname", "runNsim100.json")
experiment.base_simulation.set_parameter("customGrid", 1)
experiment.base_simulation.set_parameter("nsims", 100)

experiment.builder = builder

#platform = LocalPlatform()
platform = COMPSPlatform(endpoint="https://comps2.idmod.org", environment="Bayesian")

em = ExperimentManager(experiment=experiment, platform=platform)
em.run()
