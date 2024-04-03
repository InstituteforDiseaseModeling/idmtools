"""
        This file demonstrates how to use ExperimentBuilder in PythonExperiment's builder.
        We are then adding the builder to PythonExperiment.

        Parameters for sweeping:
            |__ a = [0,1,2,3,4]

        Expect 5 sims with config parameters, note: "b" is not a sweep parameter, but it is depending on a's value:
            sim1: {a:0, b:2}
            sim2: {a:1, b:3}
            sim3: {a:2, b:4}
            sim4: {a:3, b:5}
            sim5: {a:4, b:6}
"""

import os
import sys
from functools import partial

from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import platform
from idmtools.entities.experiment import Experiment
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_test import COMMON_INPUT_PATH


# define a custom sweep callback that sets b to a + 2
def param_update_ab(simulation, param, value):
    # Set B within
    if param == "a":
        simulation.task.set_parameter("b", value + 2)

    return simulation.task.set_parameter(param, value)


if __name__ == "__main__":
    # define what platform we want to use. Here we use a context manager but if you prefer you can
    with platform('CALCULON'):
        # define our base task
        base_task = JSONConfiguredPythonTask(script_path=os.path.join(COMMON_INPUT_PATH, "python", "model1.py"),
                                             parameters=dict(c='c-value'))

        # define our input csv sweep
        builder = SimulationBuilder()
        # Sweep parameter "a" and make "b" depends on "a"
        setAB = partial(param_update_ab, param="a")
        builder.add_sweep_definition(setAB, range(0, 5))

        # now define we want to create a series of simulations using the base task and the sweep
        ts = TemplatedSimulations.from_task(base_task, tags=dict(c='c-value'))
        ts.add_builder(builder)

        # define our experiment with its metadata
        experiment = Experiment.from_template(ts,
                                              name=os.path.split(sys.argv[0])[1],
                                              tags={"string_tag": "test", "number_tag": 123}
                                              )

        # run experiment
        experiment.run()
        # wait until done with longer interval
        # in most real scenarios, you probably do not want to wait as this will wait until all simulations
        # associated with an experiment are done. We do it in our examples to show feature and to enable
        # testing of the scripts
        experiment.wait(refresh_interval=10)
        # use system status as the exit code
        sys.exit(0 if experiment.succeeded else -1)
