import os
import sys
sys.path.append('../')
from config_update_parameters import config_update_params, param_update
from TimeseriesAnalyzer import TimeseriesAnalyzer
from functools import partial

from idmtools.assets import AssetCollection, Asset
from idmtools.builders import ExperimentBuilder
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.managers import ExperimentManager
from idmtools_model_emod import EMODExperiment
from idmtools_model_emod.defaults import EMODSir
from idmtools_model_emod.generic.serialization import add_serialization_timesteps, load_serialized_population
from idmtools.analysis.AnalyzeManager import AnalyzeManager
from idmtools.analysis.DownloadAnalyzer import DownloadAnalyzer
from idmtools_test.utils.utils import del_file, del_folder, load_csv_file


current_directory = os.path.dirname(os.path.realpath(__file__))
BIN_PATH = os.path.abspath(os.path.join(current_directory, "../bin"))
INPUT_PATH = os.path.abspath(os.path.join(current_directory, "../inputs"))
SERIALIZATION_PATH = os.path.abspath(os.path.join(current_directory, "../04_write_file_multinode/outputs"))
random_sim_id = os.listdir(SERIALIZATION_PATH)[-1]
SERIALIZATION_PATH = os.path.join(SERIALIZATION_PATH, random_sim_id)


simulation_duration = 120
num_seeds = 4
pre_serialization_day = 50
last_serialization_day = 70
expname = '05_read_file_multinode'
dtk_serialization_filename = "state-00050.dtk"
channels_tolerance = {'Statistical Population': 1,
            'Infectious Population': 0.05,
            'Waning Population': 0.05,
            'New Infections': 100,
            'Symptomatic Population': 200}


if __name__ == "__main__":

    platform = Platform('COMPS')

    ac = AssetCollection()
    dtk_file = Asset(absolute_path=os.path.join(SERIALIZATION_PATH, dtk_serialization_filename))
    ac.add_asset(dtk_file)
    #e = EMODExperiment.from_default(expname, default=EMODSir, eradication_path=os.path.join(BIN_PATH, "Eradication.exe"))
    e = EMODExperiment.from_files(expname, eradication_path=os.path.join(BIN_PATH, "Eradication.exe"),
                                  config_path=os.path.join(INPUT_PATH, 'config.json'),
                                  campaign_path=os.path.join(INPUT_PATH, "campaign.json"),
                                  demographics_paths=os.path.join(INPUT_PATH, "9nodes_demographics.json"))
    e.add_assets(ac)
    simulation = e.base_simulation

    #Update bunch of config parameters
    sim = config_update_params(simulation)

    add_serialization_timesteps(sim=sim, timesteps=[last_serialization_day],
                                end_at_final=False, use_absolute_times=True)
    load_serialized_population(sim=sim, population_path="Assets", population_filenames=[dtk_serialization_filename])

    sim.update_parameters({
        "Start_Time": pre_serialization_day,
        "Simulation_Duration":  simulation_duration - pre_serialization_day,
        "Config_Name": 'Generic serialization 05 read files multinode',
        "Demographics_Filenames": ["9nodes_demographics.json"]})

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

        pre_exp_id = platform.get_parent(random_sim_id, ItemType.SIMULATION).uid
        print(f"Running TimeseriesAnalyzer with experiment id: {exp_id} and {pre_exp_id}:\n")
        analyzers_timeseries = [TimeseriesAnalyzer(filenames=['output/InsetChart.json'])]
        am_timeseries = AnalyzeManager(platform=platform,
                                       ids=[(exp_id, ItemType.EXPERIMENT),
                                            (pre_exp_id, ItemType.EXPERIMENT)],
                                       analyzers=analyzers_timeseries)
        am_timeseries.analyze()

        df = load_csv_file(filename = 'timeseries_diff.csv')
        with open("result.txt", "w") as result_file:
            if df is not None and not df.empty:
                for channel, tolerance in channels_tolerance.items():
                    if any(df[channel] > tolerance):
                        result_file.write(f"BAD: {channel} channel in InetChart.json from both experiments has large "
                                          f"gap({df[channel].max()}), please see timeseries.png.\n")
                    else:
                        result_file.write(f"GOOD: {channel} channel in InetChart.json from both experiments has small"
                                          f" gap({df[channel].max()}), please see timeseries.png.\n")
            else:
                result_file.write("# of Experiments > 2, we don't compare the difference, please see timeseries.png.\n ")

        print("Downloading dtk serialization files from Comps:\n")
        filenames = ['output/InsetChart.json', "output/state-000" +
                     str(last_serialization_day - pre_serialization_day) + ".dtk"]
        output_path = 'outputs'
        if os.path.isdir(output_path):
            del_folder(output_path)
        analyzers_download = [DownloadAnalyzer(filenames=filenames, output_path=output_path)]
        am_download = AnalyzeManager(platform=platform, ids=[(exp_id, ItemType.EXPERIMENT)],
                                     analyzers=analyzers_download)
        am_download.analyze()

    else:
        print(f"Experiment {exp_id} failed.\n")

