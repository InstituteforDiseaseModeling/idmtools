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

from idmtools.builders import SweepArm, ArmType, ArmExperimentBuilder
from idmtools.core.platform_factory import Platform
from idmtools.managers import ExperimentManager
from idmtools_models.python import PythonExperiment
from idmtools_test import COMMON_INPUT_PATH


def param_update(simulation, param, value):
    return simulation.set_parameter(param, value)


setA = partial(param_update, param="a")
setB = partial(param_update, param="b")
setC = partial(param_update, param="c")


if __name__ == "__main__":
    platform = Platform('COMPS2')
    pe = PythonExperiment(name=os.path.split(sys.argv[0])[1],
                          model_path=os.path.join(COMMON_INPUT_PATH, "python", "model1.py"))
    pe.tags = {"idmtools": "idmtools-automation", "string_tag": "test", "number_tag": 123, "KeyOnly": None}

    arm1 = SweepArm(type=ArmType.cross)
    builder = ArmExperimentBuilder()
    arm1.add_sweep_definition(setA, 1)
    arm1.add_sweep_definition(setB, [2, 3])
    arm1.add_sweep_definition(setC, [4, 5])
    builder.add_arm(arm1)

    # adding more simulations with sweeping
    arm2 = SweepArm(type=ArmType.cross)
    arm2.add_sweep_definition(setA, [6, 7])
    arm2.add_sweep_definition(setB, [2])
    builder.add_arm(arm2)
    pe.builder = builder
    em = ExperimentManager(experiment=pe, platform=platform)
    em.run()
    em.wait_till_done()
