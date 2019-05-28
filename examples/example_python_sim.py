import os
from functools import partial

from entities.IExperimentBuilder import IExperimentBuilder
from managers.ExperimentManager import ExperimentManager
from platforms.COMPSPlatform import COMPSPlatform
from platforms.LocalPlatform import LocalPlatform
from python.PythonExperiment import PythonExperiment


def param_update(simulation, param, value):
    return simulation.set_parameter(param, value)


experiment = PythonExperiment(name="My First experiment", model_path=os.path.join("inputs", "model.py"))
experiment.tags["tag1"] = 1
experiment.base_simulation.set_parameter("c", 0)
experiment.assets.add_directory(assets_directory=os.path.join("inputs", "Assets"))

setA = partial(param_update, param="a")

class setB:
    def __init__(self, param):
        self.param = param

    def __call__(self, simulation, value):
        return param_update(simulation, self.param, value)


builder = IExperimentBuilder()
builder.add_sweep_definition(setA, range(100))
builder.add_sweep_definition(setB("b"), [1, 2, 3])

experiment.builder = builder

platform = COMPSPlatform()

em = ExperimentManager(experiment=experiment, platform=platform)
em.run()
