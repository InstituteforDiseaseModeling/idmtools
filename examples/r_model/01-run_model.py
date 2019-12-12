import itertools
import os
import shutil
from typing import NoReturn

import numpy as np
from idmtools.builders import ExperimentBuilder
from idmtools.core.platform_factory import Platform
from idmtools.managers import ExperimentManager
from idmtools_models.r.r_experiment import RExperiment


def sum_to_n(sum_to, spaced_samples=10, dimensions=3):
    for cuts in itertools.permutations(np.linspace(0, sum_to, spaced_samples), dimensions):
        # only return when the cut adds up to one and infections(index 0) is greater than 0
        if sum(cuts) == sum_to and all([x > 0 for x in cuts]):
            yield cuts


def save_experiment_id(experiment_id: str, update_latest: bool = True) -> NoReturn:
    """
    Save an experiment to the current directory as {filename}.experiment.{exp_id} and {filename}.experiment.{latest}.
    This allows more predictable workflows by allowing other scripts reference output experiment from this script in the
    future while also being able to reference the latest experiment id as well


    Args:
        experiment_id:
        update_latest
    Returns:
        NoReturn
    """
    # get last run id
    base_exp_fn = f'{__file__.replace(".py", "")}.experiment.'
    out_name = f'{base_exp_fn}{experiment_id}'
    # now write the the latest and copy to number file
    with open(out_name, 'w') as out:
        out.write(experiment_id)

    # check if we already have a latest. If we do, overwrite
    if update_latest:
        latest_fn = f"{base_exp_fn}latest"
        if os.path.exists(latest_fn):
            os.remove(latest_fn)

        shutil.copy(out_name, latest_fn)


def param_update(simulation, value):
    result = simulation.set_parameter('infections', value[0])
    result.update(simulation.set_parameter('recovered', value[1]))
    result.update(simulation.set_parameter('susceptible', value[2]))
    return result


# the image_name is the same name of the image we tagged when we built our Dockerfile.
# since we used docker-compose, it is the image options in the definition of the service
experiment = RExperiment(name="R SIR",
                         image_name='idm-docker-staging.idmod.org/idmtools_r_model_example:latest',
                         config_param='--config-file',
                         build=True,
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
save_experiment_id(experiment.uid)
