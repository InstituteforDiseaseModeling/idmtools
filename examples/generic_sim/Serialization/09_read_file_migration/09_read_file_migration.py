import os
import sys
sys.path.append('../')
from config_update_parameters import config_update_params, param_update
from TimeseriesAnalyzer import TimeseriesAnalyzer
from NodeDemographicsAnalyzer import NodeDemographicsAnalyzer
from functools import partial

from idmtools.assets import AssetCollection
from idmtools.builders import ExperimentBuilder
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.core import FilterMode
from idmtools.managers import ExperimentManager
from idmtools_model_emod import EMODExperiment
from idmtools_model_emod.defaults import EMODSir
from idmtools_model_emod.generic.serialization import add_serialization_timesteps, load_serialized_population
from idmtools.analysis.AnalyzeManager import AnalyzeManager
from idmtools.analysis.DownloadAnalyzer import DownloadAnalyzer
from idmtools_test.utils.utils import del_folder, load_csv_file
from idmtools.utils.filters.asset_filters import file_name_is


current_directory = os.path.dirname(os.path.realpath(__file__))
BIN_PATH = os.path.abspath(os.path.join(current_directory, "../bin"))
INPUT_PATH = os.path.abspath(os.path.join(current_directory, "../inputs"))
SERIALIZATION_PATH = os.path.abspath(os.path.join(current_directory, "../08_write_file_migration/outputs"))
random_sim_id = os.listdir(SERIALIZATION_PATH)[-1]
SERIALIZATION_PATH = os.path.join(SERIALIZATION_PATH, random_sim_id)

simulation_duration = 120
num_seeds = 1
pre_serialization_day = 50
last_serialization_day = 70
expname = '09_read_file_migration'
dtk_serialization_filename = "state-00050.dtk"
dtk_migration_filenames = ["LocalMigration_3_Nodes.bin", "LocalMigration_3_Nodes.bin.json"]

channels_tolerance = {'Statistical Population': 1,
            'Infectious Population': 0.05,
            'Waning Population': 0.05,
            'New Infections': 50,
            'Symptomatic Population': 100}
node_columns_tolerance = {'NumIndividuals': 30, 'NumInfected': 40}


if __name__ == "__main__":

    platform = Platform('COMPS')

    ac = AssetCollection()
    filter_name_s = partial(file_name_is, filenames=[dtk_serialization_filename])
    ac.add_directory(assets_directory=SERIALIZATION_PATH, filters=[filter_name_s], filters_mode= FilterMode.OR)
    filter_name_m = partial(file_name_is, filenames=dtk_migration_filenames)
    ac.add_directory(assets_directory=INPUT_PATH, filters=[filter_name_m], filters_mode=FilterMode.OR)
    # e = EMODExperiment.from_default(expname, default=EMODSir, eradication_path=os.path.join(BIN_PATH, "Eradication.exe"))
    e = EMODExperiment.from_files(expname, eradication_path=os.path.join(BIN_PATH, "Eradication.exe"),
                                  config_path=os.path.join(INPUT_PATH, 'config.json'),
                                  campaign_path=os.path.join(INPUT_PATH, "campaign.json"),
                                  demographics_paths=os.path.join(INPUT_PATH, "3nodes_demographics.json"))

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
        "Config_Name": 'Generic serialization 09 read files migration',
        "Migration_Model": "FIXED_RATE_MIGRATION",
        "Migration_Pattern": "RANDOM_WALK_DIFFUSION",
        "Local_Migration_Filename": "Assets/LocalMigration_3_Nodes.bin",
        "Enable_Local_Migration": 1,
        "Enable_Air_Migration": 0,
        "Enable_Family_Migration": 0,
        "Enable_Migration_Heterogeneity": 0,
        "Enable_Regional_Migration": 0,
        "Enable_Sea_Migration": 0,
        "x_Local_Migration": 0.1
        })

    sim.add_custom_reports(custom_reports_file="../custom_reports/custom_reports.json")
    e.add_dll_files(dll_files_path="../custom_reports")


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

        pre_exp_id = "2ba8a82f-8e01-ea11-a2be-f0921c167861"
        #pre_exp_id = platform.get_parent(random_sim_id, ItemType.SIMULATION).uid
        print(f"Running NodeDemographicsAnalyzer with experiment id: {exp_id} and {pre_exp_id}:\n")
        analyzers_nd = [NodeDemographicsAnalyzer(filenames=['output/ReportNodeDemographics.csv'])]
        am_nd = AnalyzeManager(platform=platform,
                                       ids=[(exp_id, ItemType.EXPERIMENT),
                                            (pre_exp_id, ItemType.EXPERIMENT)],
                                       analyzers=analyzers_nd)
        am_nd.analyze()
        with open("node_demographics_result.txt", "w") as nd_result_file:
            for node_column, tolerance in node_columns_tolerance.items():
                node_df = load_csv_file(filename=str(node_column) + '_node_demographics_diff.csv')
                if node_df is not None and not node_df.empty:
                    for column in node_df.columns:
                        if column != 'Time':
                            if any(node_df[column] > tolerance):
                                nd_result_file.write(f"BAD: {node_column}_{column} in ReportNodeDemographics.csv from"
                                                     f" both experiments has large gap(max={node_df[column].max()}), "
                                                     f"please see node_demographics.png.\n")
                            else:
                                nd_result_file.write(f"GOOD: {node_column}_{column} in ReportNodeDemographics.csv from"
                                                     f" both experiments has small gap(max={node_df[column].max()}), "
                                                     f"please see node_demographics.png.\n")
                else:
                    nd_result_file.write("# of Experiments > 2, we don't compare the difference, "
                                         "please see node_demographics.png.\n")


        print(f"Running TimeseriesAnalyzer with experiment id: {exp_id} and {pre_exp_id}:\n")
        analyzers_ts = [TimeseriesAnalyzer(filenames=['output/InsetChart.json'])]#, channels=[])]
        am_ts = AnalyzeManager(platform=platform,
                                       ids=[(exp_id, ItemType.EXPERIMENT),
                                            (pre_exp_id, ItemType.EXPERIMENT)],
                                       analyzers=analyzers_ts)
        am_ts.analyze()

        df = load_csv_file(filename = 'timeseries_diff.csv')
        with open("timeseries_result.txt", "w") as ts_file:
            if df is not None and not df.empty:
                for channel, tolerance in channels_tolerance.items():
                    if any(df[channel] > tolerance):
                        ts_file.write(f"BAD: {channel} channel in InetChart.json from both experiments has large "
                                      f"gap(max={df[channel].max()}), please see timeseries.png.\n")
                    else:
                        ts_file.write(f"GOOD: {channel} channel in InetChart.json from both experiments has small "
                                      f"gap(max={df[channel].max()}), please see timeseries.png.\n")
            else:
                ts_file.write("# of Experiments > 2, we don't compare the difference, please see timeseries.png.\n")

        print("Downloading dtk serialization files from Comps:\n")

        filenames = ['output/InsetChart.json',
                     'output/ReportHumanMigrationTracking.csv',
                     'output/ReportNodeDemographics.csv',
                     f"output/state-000{last_serialization_day - pre_serialization_day}.dtk"]
        output_path = 'outputs'
        if os.path.isdir(output_path):
            del_folder(output_path)
        analyzers_download = [DownloadAnalyzer(filenames=filenames, output_path=output_path)]
        am_download = AnalyzeManager(platform=platform, ids=[(exp_id, ItemType.EXPERIMENT)],
                                     analyzers=analyzers_download)
        am_download.analyze()

    else:
        print(f"Experiment {exp_id} failed.\n")

