import os
import sys
from functools import partial

from idmtools.builders import StandAloneSimulationsBuilder, SweepArm, ArmType, ArmExperimentBuilder
from idmtools.core.platform_factory import Platform
from idmtools.managers import ExperimentManager
from idmtools_model_emod import EMODExperiment
from idmtools_model_emod.defaults import EMODSir
from idmtools_test import COMMON_INPUT_PATH

def param_update(simulation, param, value):
    return simulation.set_parameter(param, value)

if __name__ == "__main__":
    platform = Platform('COMPS')
    experiment = EMODExperiment.from_default(name=os.path.split(sys.argv[0])[1], default=EMODSir(),
                                             eradication_path=os.path.join(COMMON_INPUT_PATH, "emod", "Eradication.exe"))

    experiment.base_simulation.load_files(config_path=os.path.join(COMMON_INPUT_PATH, "files", "config.json"),
                                          campaign_path=os.path.join(COMMON_INPUT_PATH, "files", "campaign.json"))

    experiment.demographics.add_demographics_from_file(
        os.path.join(COMMON_INPUT_PATH, "files", "demographics.json"))

    arm = SweepArm(type=ArmType.cross)
    set_Run_Number = partial(param_update, param="Run_Number")
    arm.add_sweep_definition(set_Run_Number, range(10))

    set_x_Temporary_Larval_Habitat = partial(param_update, param="x_Temporary_Larval_Habitat")
    arm.add_sweep_definition(set_x_Temporary_Larval_Habitat, [0.1, 0.2])

    builder = ArmExperimentBuilder()
    builder.add_arm(arm)
    experiment.builder = builder

    em = ExperimentManager(experiment=experiment, platform=platform)
    em.run()
    em.wait_till_done()
