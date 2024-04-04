"""
        This file demonstrates how to use ArmExperimentBuilder in PythonExperiment's builder.
        We are then adding the builder to PythonExperiment.

        |__sweep arm1
            |_ a = 1
            |_ b = [2,3]
            |_ c = [4,5]
        |__ sweep arm2
            |_ a = [6,7]
            |_ b = 2
        Expect sims with parameters:
            sim1: {a:1, b:2, c:4}
            sim2: {a:1, b:2, c:5}
            sim3: {a:1, b:3, c:4}
            sim4: {a:1, b:3, c:5}
            sim5: {a:6, b:2}
            sim6: {a:7, b:2}
        Note:
            arm1 and arm2 are adding to total simulations
"""
import os
import sys
from functools import partial

from idmtools.builders import SweepArm, ArmType, ArmSimulationBuilder
from idmtools.core.platform_factory import platform
from idmtools.entities.experiment import Experiment
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_test import COMMON_INPUT_PATH

# define specific callbacks for a, b, and c
setA = partial(JSONConfiguredPythonTask.set_parameter_sweep_callback, param="a")
setB = partial(JSONConfiguredPythonTask.set_parameter_sweep_callback, param="b")
setC = partial(JSONConfiguredPythonTask.set_parameter_sweep_callback, param="c")


if __name__ == "__main__":
    with platform('CALCULON'):
        base_task = JSONConfiguredPythonTask(script_path=os.path.join(COMMON_INPUT_PATH, "python", "model1.py"))
        # define that we are going to create multiple simulations from this task
        ts = TemplatedSimulations(base_task=base_task)

        # define our first sweep Sweep Arm
        arm1 = SweepArm(type=ArmType.cross)
        builder = ArmSimulationBuilder()
        arm1.add_sweep_definition(setA, 1)
        arm1.add_sweep_definition(setB, [2, 3])
        arm1.add_sweep_definition(setC, [4, 5])
        builder.add_arm(arm1)

        # adding more simulations with sweeping
        arm2 = SweepArm(type=ArmType.cross)
        arm2.add_sweep_definition(setA, [6, 7])
        arm2.add_sweep_definition(setB, [2])
        builder.add_arm(arm2)

        # add our builders to our template
        ts.add_builder(builder)

        # create experiment from the template
        experiment = Experiment.from_template(ts, name=os.path.split(sys.argv[0])[1],
                                              tags={"string_tag": "test", "number_tag": 123, "KeyOnly": None})
        # run the experiment
        experiment.run()
        # in most real scenarios, you probably do not want to wait as this will wait until all simulations
        # associated with an experiment are done. We do it in our examples to show feature and to enable
        # testing of the scripts
        experiment.wait()
        # use system status as the exit code
        sys.exit(0 if experiment.succeeded else -1)
