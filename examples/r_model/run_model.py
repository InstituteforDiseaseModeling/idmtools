import os
import numpy as np
from idmtools.builders import ExperimentBuilder
from idmtools.core.platform_factory import Platform
from idmtools.managers import ExperimentManager
from idmtools_models.r.r_experiment import RExperiment


def param_update(simulation, param, value):
    return simulation.set_parameter(param, value)

# the image_name is the same name of the image we tagged when we built our Dockerfile.
# since we used docker-compose, it is the image options in the definition of the service
experiment = RExperiment(name="My First experiment",
                         image_name='idm-docker-staging.idmod.org/idmtools_r_model_example:latest',
                         model_path=os.path.join("work", "inputs", "python_model_with_deps", "Assets", "model_R.py"))
experiment.tags["tag1"] = 1
experiment.base_simulation.set_parameter("infections", 0.0001)


class setParam:
    def __init__(self, param):
        self.param = param

    def __call__(self, simulation, value):
        return param_update(simulation, self.param, value)


builder = ExperimentBuilder()
builder.add_sweep_definition(setParam("infections"), np.linspace(0, 1, 3))
builder.add_sweep_definition(setParam("recovered"), np.linspace(0, 1, 3))
builder.add_sweep_definition(setParam("susceptible"), np.linspace(0, 1, 3))

experiment.add_builder(builder)

platform = Platform('Local')

em = ExperimentManager(experiment=experiment, platform=platform)
em.run()
em.wait_till_done()
