import itertools
import os
import shutil
import sys
from typing import NoReturn, Tuple, Dict

import numpy as np

from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import platform
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.r.json_r_task import JSONConfiguredRTask


def sum_to_n(sum_to, spaced_samples=10, dimensions=3):
    """
    Get permutations

    Args:
        sum_to:
        spaced_samples:
        dimensions:

    Returns:

    """
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


def param_update(simulation: Simulation, value: Tuple[float, float, float]) -> Dict[str, float]:
    """
    Custom Sweep function that
    Args:
        simulation:
        value:

    Returns:

    """
    result = simulation.task.set_parameter('infections', value[0])
    result.update(simulation.task.set_parameter('recovered', value[1]))
    result.update(simulation.task.set_parameter('susceptible', value[2]))
    return dict(infections=value[0], recovered=value[1], susceptible=value[2])


# the image_name is the same name of the image we tagged when we built our Dockerfile.
# since we used docker-compose, it is the image options in the definition of the service
with platform("Local"):
    base_task = JSONConfiguredRTask(
        # path to R Script
        script_name=os.path.abspath(os.path.join('model', 'model.r')),
        # Argument name the script file expects
        configfile_argument='--config-file',
        # should we build the R image before attempting to run
        build=True,
        # what docker image name should we save/load
        # TODO how to handle build tag vs run tag? We prefer running with docker-staging not idm-docker-stagin
        image_name='idm-docker-staging.idmod.org/idmtools/r_model_example:latest',
        # default parameters
        parameters=dict(infections=0.0001)
    )

    # create templates simulations object
    ts = TemplatedSimulations(base_task=base_task)

    # create sweep
    builder = SimulationBuilder()
    builder.add_sweep_definition(param_update, list(sum_to_n(1)))
    ts.add_builder(builder)

    e = Experiment.from_template(ts, tags=dict(tag1=1))
    e.run(wait_until_done=True)

    save_experiment_id(e.uid)
    sys.exit(0 if e.succeeded else -1)
