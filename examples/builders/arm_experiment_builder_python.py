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

# |__ A = 1
#      |_ B = [2,3]
#      |_ C = [4,5]
# |__ A = [6,7]
#    |_ B = 2
# expect sims with parameters:
# {1,2,4}
# {1,2,5}
# {1,3,4}
# {1,3,5}
# {6,2}
# {7,2}
if __name__ == "__main__":
    platform = Platform('COMPS')
    pe = PythonExperiment(name=os.path.split(sys.argv[0])[1],
                          model_path=os.path.join(COMMON_INPUT_PATH, "python", "model1.py"))
    pe.tags = {"idmtools": "idmtools-automation", "string_tag": "test", "number_tag": 123, "KeyOnly": None}

    arm = SweepArm(type=ArmType.cross)
    builder = ArmExperimentBuilder()
    arm.add_sweep_definition(setA, 1)
    arm.add_sweep_definition(setB, [2, 3])
    arm.add_sweep_definition(setC, [4, 5])
    builder.add_arm(arm)
    arm = SweepArm(type=ArmType.cross)
    arm.add_sweep_definition(setA, [6, 7])
    arm.add_sweep_definition(setB, [2])
    builder.add_arm(arm)
    pe.builder = builder
    em = ExperimentManager(experiment=pe, platform=platform)
    em.run()
    em.wait_till_done()
