import os
from functools import partial

from idmtools.builders import ExperimentBuilder
from idmtools.core.platform_factory import Platform
from idmtools.managers import ExperimentManager

from idmtools_models.python.python_experiment import PythonExperiment


def param_update(simulation, param, value):
    return simulation.set_parameter(param, value)


experiment = PythonExperiment(name="My First experiment", model_path=os.path.join("work", "inputs", "python_model_with_deps", "Assets", "model.py"))
experiment.tags["tag1"] = 1
experiment.base_simulation.set_parameter("c", 0)
experiment.assets.add_directory(assets_directory=os.path.join("work", "inputs", "python_model_with_deps", "Assets"))

setA = partial(param_update, param="a")


class setParam:
    def __init__(self, param):
        self.param = param

    def __call__(self, simulation, value):
        return param_update(simulation, self.param, value)


builder = ExperimentBuilder()
builder.add_sweep_definition(setA, range(10))
builder.add_sweep_definition(setParam("b"), [1, 2, 3])

experiment.add_builder(builder)

platform = Platform('COMPS2')
# You can easily switch platforms by simply commenting out the previous line and then
# uncommenting the following line
# platform = Platform('COMPS')

em = ExperimentManager(experiment=experiment, platform=platform)
em.run()
em.wait_till_done()
