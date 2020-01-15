import os
import sys

from idmtools.builders import StandAloneSimulationsBuilder
from idmtools.core.platform_factory import Platform
from idmtools.managers import ExperimentManager
from idmtools_model_emod import EMODExperiment
from idmtools_model_emod.defaults import EMODSir
from idmtools_test import COMMON_INPUT_PATH

if __name__ == "__main__":
    platform = Platform('COMPS')
    experiment = EMODExperiment.from_default(name=os.path.split(sys.argv[0])[1], default=EMODSir(),
                                             eradication_path=os.path.join(COMMON_INPUT_PATH, "emod",
                                                                           "Eradication.exe"))

    experiment.base_simulation.load_files(config_path=os.path.join(COMMON_INPUT_PATH, "files", "config.json"),
                                          campaign_path=os.path.join(COMMON_INPUT_PATH, "files", "campaign.json"))

    experiment.demographics.add_demographics_from_file(
        os.path.join(COMMON_INPUT_PATH, "files", "demographics.json"))

    b = StandAloneSimulationsBuilder()
    for i in range(10):
        sim = experiment.simulation()
        sim.set_parameter("Enable_Immunity", 0)
        sim.set_parameter("Infectious_Period_Exponential", 5)
        b.add_simulation(sim)
    experiment.builder = b

    em = ExperimentManager(experiment=experiment, platform=platform)
    em.run()
    em.wait_till_done()
