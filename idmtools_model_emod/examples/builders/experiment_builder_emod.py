"""
        This file demonstrates how to use ExperimentBuilder in EMODExperiment's builder.
        We are then adding the builder to EMODExperiment.

        Parameters for sweeping:
            |__ Run_Number = [0,1,2,3,4]
            |__ x_Temporary_Larval_Habitat = [0.1,0.2]
            |__ test_tag = ["abcd"]

        Expect 10 sims with config parameters:
            sim1: {Run_Number: 0, x_Temporary_Larval_Habitat: 0.1, test_tag:"abcd"}
            sim2: {Run_Number: 0, x_Temporary_Larval_Habitat: 0.2, test_tag:"abcd"}
            sim3: {Run_Number: 1, x_Temporary_Larval_Habitat: 0.1, test_tag:"abcd"}
            sim4: {Run_Number: 1, x_Temporary_Larval_Habitat: 0.2, test_tag:"abcd"}
            ....
            sim8: {Run_Number: 4, x_Temporary_Larval_Habitat: 0.1, test_tag:"abcd"}
            sim9: {Run_Number: 4, x_Temporary_Larval_Habitat: 0.2, test_tag:"abcd"}
"""

import os
import sys
from functools import partial

from idmtools.managers import ExperimentManager

from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools_model_emod import EMODExperiment
from idmtools_model_emod.defaults import EMODSir
from idmtools_test import COMMON_INPUT_PATH


def param_update(simulation, param, value):
    return simulation.set_parameter(param, value)


if __name__ == "__main__":
    platform = Platform('COMPS2')
    experiment = EMODExperiment.from_default(name=os.path.split(sys.argv[0])[1], default=EMODSir(),
                                             eradication_path=os.path.join(COMMON_INPUT_PATH, "emod",
                                                                           "Eradication.exe"))

    experiment.base_simulation.load_files(config_path=os.path.join(COMMON_INPUT_PATH, "files", "config.json"),
                                          campaign_path=os.path.join(COMMON_INPUT_PATH, "files", "campaign.json"))

    experiment.demographics.add_demographics_from_file(
        os.path.join(COMMON_INPUT_PATH, "files", "demographics.json"))

    # Sweep parameters
    builder = SimulationBuilder()
    set_Run_Number = partial(param_update, param="Run_Number")
    builder.add_sweep_definition(set_Run_Number, range(5))
    experiment.tags = {'idmtools': 'create_serialization'}
    set_x_Temporary_Larval_Habitat = partial(param_update, param="x_Temporary_Larval_Habitat")
    builder.add_sweep_definition(set_x_Temporary_Larval_Habitat, [0.1, 0.2])

    # Add simulation tags
    experiment.base_simulation.tags = {'add_base_sim_tag': 'my_tag'}
    # another way to add custom simulation tags with add_sweep_definition
    set_tag = partial(param_update, param="test_tag")
    builder.add_sweep_definition(set_tag, "abcd")

    experiment.builder = builder
    em = ExperimentManager(experiment=experiment, platform=platform)
    em.run()
    em.wait_till_done()
