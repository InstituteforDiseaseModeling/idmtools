"""
This file demonstrates doing a multi-argument sweep

Sometimes you need multiple parameters at the same time, usually to create objects within a callback. The *
"""

import os
import sys
from dataclasses import dataclass
from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_test import COMMON_INPUT_PATH


@dataclass
class ModelConfig:
    a: int
    b: int
    c: int


# define a custom sweep callback that sets b to a + 2
def param_update(simulation, a_value, b_value, c_value):
    mc = ModelConfig(a_value, b_value, c_value)
    simulation.task.set_parameter('a', mc.a)
    simulation.task.set_parameter('b', mc.b)
    simulation.task.set_parameter('c', mc.c)
    return dict(a=a_value, b=b_value, c=c_value)


if __name__ == "__main__":
    # define what platform we want to use. Here we use a context manager but if you prefer you can
    # use objects such as Platform('Calculon') instead
    with Platform('Calculon'):
        # define our base task
        base_task = JSONConfiguredPythonTask(script_path=os.path.join(COMMON_INPUT_PATH, "python", "model1.py"),
                                             parameters=dict())
        # define our input csv sweep
        builder = SimulationBuilder()
        # we can use add_sweep_definition call to do multiple parameter sweeping now
        builder.add_sweep_definition(param_update, range(2), range(2), range(2))
        #builder.add_multiple_parameter_sweep_definition(param_update, range(2), range(2), range(2))

        # define our experiment with its metadata
        experiment = Experiment.from_builder(
            builders=[builder], base_task=base_task,
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
