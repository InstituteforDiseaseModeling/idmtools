import os
from idmtools.core.platform_factory import Platform
from idmtools.managers import ExperimentManager
from idmtools_model_emod import EMODExperiment
from idmtools_model_emod.defaults import EMODSir

CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
INPUT_PATH = os.path.join(CURRENT_DIRECTORY, "inputs")
BIN_PATH = os.path.join(CURRENT_DIRECTORY, "bin")

sim_duration = 10  # in years
num_seeds = 5

expname = 'example_multiple_demographics'


def param_update(simulation, param, value):
    return simulation.set_parameter(param, value)


if __name__ == "__main__":
    platform = Platform('COMPS')

    demo_files = [os.path.join(INPUT_PATH, "PFA_rates_overlay.json"),
                  os.path.join(INPUT_PATH, "pfa_simple.json"),
                  os.path.join(INPUT_PATH, "uniform_demographics.json"),
                  os.path.join(INPUT_PATH, "demographics.json")]

    # Case: from_files
    # e = EMODExperiment.from_files(expname,
    #                              eradication_path=os.path.join(INPUT_PATH, "Eradication.exe"),
    #                              config_path=os.path.join(INPUT_PATH, "config.json"),
    #                              campaign_path=os.path.join(INPUT_PATH, "campaign.json"),
    #                              demographics_paths=demo_files)

    # Succeeded with this exe
    e = EMODExperiment.from_default(expname, default=EMODSir,
                                    eradication_path=os.path.join(INPUT_PATH, "Eradication.exe"))

    # Failed EMODExperiment this exe
    # e = EMODExperiment.from_default(expname, default=EMODSir,
    #                                eradication_path=os.path.join(BIN_PATH, "Eradication.exe"))

    # Case: load demographics from experiment
    e.from_files(expname, config_path=os.path.join(INPUT_PATH, "config.json"),
                 campaign_path=os.path.join(INPUT_PATH, "campaign.json"),
                 demographics_paths=demo_files)

    # Case: load demographics from simulation
    # e.base_simulation.load_files(config_path=os.path.join(INPUT_PATH, "config.json"),
    #                              campaign_path=os.path.join(INPUT_PATH, "campaign.json"),
    #                              demographics_paths=demo_files)

    em = ExperimentManager(experiment=e, platform=platform)
    em.run()
    em.wait_till_done()
