import os
import sys
sys.path.append('../')
from config_update_parameters import config_update_params, param_update
import numpy as np
from functools import partial

from idmtools.assets import AssetCollection, Asset
from idmtools.builders import ExperimentBuilder
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.managers import ExperimentManager
from idmtools_model_emod import EMODExperiment
from idmtools_model_emod.defaults import EMODSir
from idmtools_model_emod.generic.serialization import add_serialization_timesteps
from idmtools.analysis.AnalyzeManager import AnalyzeManager
from idmtools.analysis.DownloadAnalyzer import DownloadAnalyzer
from idmtools_test.utils.utils import del_file, del_folder, load_csv_file


current_directory = os.path.dirname(os.path.realpath(__file__))
BIN_PATH = os.path.abspath(os.path.join(current_directory, "../bin"))
INPUT_PATH = os.path.abspath(os.path.join(current_directory, "../inputs"))

start_day = 0
simulation_duration = 120
num_seeds = 4
num_cores = 4
last_serialization_day = 70
expname = '06_write_file_multicore'


if __name__ == "__main__":

    platform = Platform('COMPS-Multicore-Linux')

    e = EMODExperiment.from_files(expname, eradication_path=os.path.join(BIN_PATH, "Eradication"),
                                  config_path=os.path.join(INPUT_PATH, 'config.json'),
                                  campaign_path=os.path.join(INPUT_PATH, "campaign.json"),
                                  demographics_paths=os.path.join(INPUT_PATH, "9nodes_demographics.json"))
    # e = EMODExperiment.from_default(expname, default=EMODSir, eradication_path=os.path.join(BIN_PATH,
    #                                                                                         "Eradication.exe"))
    simulation = e.base_simulation
    # simulation.load_files(campaign_path=os.path.join(INPUT_PATH, "campaign.json"))

    #Update bunch of config parameters
    sim = config_update_params(simulation)

    serialization_timesteps = np.append(np.arange(10, last_serialization_day, 20), last_serialization_day).tolist()
    add_serialization_timesteps(sim=sim, timesteps=serialization_timesteps,
                                end_at_final=False, use_absolute_times=False)

    sim.update_parameters({
        "Start_Time": start_day,
        "Simulation_Duration": simulation_duration,
        "Config_Name": 'Generic serialization 06 writes files multicore',
        "Num_Cores": num_cores})
    # e.demographics.add_demographics_from_file(os.path.join(INPUT_PATH, "9nodes_demographics.json"))

    builder = ExperimentBuilder()
    set_Run_Number = partial(param_update, param="Run_Number")
    builder.add_sweep_definition(set_Run_Number, range(num_seeds))

    e.builder = builder
    em = ExperimentManager(experiment=e, platform=platform)
    em.run()
    em.wait_till_done()
    exp_id = em.experiment.uid

    if e.succeeded:
        print(f"Experiment {exp_id} succeeded.\n")
        print("Downloading dtk serialization files from Comps:\n")
        filenames = []
        for serialization_timestep in serialization_timesteps:
            for i in range(num_cores):
                filenames.append("output/state-000" + str(serialization_timestep) + f"-00{i}" + ".dtk")
        filenames.append('output/InsetChart.json')
        output_path = 'outputs'
        if os.path.isdir(output_path):
            del_folder(output_path)

        analyzers = [DownloadAnalyzer(filenames=filenames, output_path=output_path)]

        am = AnalyzeManager(platform=platform, ids=[(exp_id, ItemType.EXPERIMENT)], analyzers=analyzers)
        am.analyze()
    else:
        print(f"Experiment {exp_id} failed.\n")

