import itertools
import operator
import os
import numpy as np
from idmtools.builders import ExperimentBuilder
from idmtools.core.platform_factory import Platform
from idmtools.managers import ExperimentManager
from idmtools_models.r.r_experiment import RExperiment


def sum_to_n(sum_to, spaced_samples=10, dimensions=3):
    for cuts in itertools.permutations(np.linspace(0, sum_to, spaced_samples), dimensions):
        # only return when the cut adds up to one and infections(index 0) is greater than 0
        if sum(cuts) == sum_to and cuts[0] > 0:
            yield cuts


def param_update(simulation, value):
    result = simulation.set_parameter('infections', value[0])
    result.update(simulation.set_parameter('recovered', value[1]))
    result.update(simulation.set_parameter('susceptible', value[2]))
    return result


# the image_name is the same name of the image we tagged when we built our Dockerfile.
# since we used docker-compose, it is the image options in the definition of the service
experiment = RExperiment(name="My First experiment",
                         image_name='idm-docker-staging.idmod.org/idmtools_r_model_example:latest',
                         config_param='--config-file',
                         model_path=os.path.join("model.R"))
experiment.tags["tag1"] = 1
experiment.base_simulation.set_parameter("infections", 0.0001)


builder = ExperimentBuilder()
builder.add_sweep_definition(param_update, list(sum_to_n(1)))


experiment.add_builder(builder)

platform = Platform('Local')

em = ExperimentManager(experiment=experiment, platform=platform)
em.run()
em.wait_till_done()
