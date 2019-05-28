import os
from functools import partial

from interfaces.IExperimentBuilder import IExperimentBuilder
from managers.ExperimentManager import ExperimentManager
from platforms.LocalPlatform import LocalPlatform
from python.PythonExperiment import PythonExperiment


def param_update(simulation, param, value):
    return simulation.set_parameter(param, value)


experiment = PythonExperiment(name="My First experiment", model_path=os.path.join("inputs", "model.py"))
experiment.tags["tag1"] = 1
experiment.base_simulation.set_parameter("c", 0)
experiment.assets.add_directory(assets_directory=os.path.join("inputs", "Assets"))

setA = partial(param_update, param="a")
setB = partial(param_update, param="b")

builder = IExperimentBuilder()
builder.add_sweep_definition(setA, range(100))
builder.add_sweep_definition(setB, [1, 2, 3])

experiment.builder = builder

platform = LocalPlatform()

em = ExperimentManager(experiment=experiment, platform=platform)
em.run()
