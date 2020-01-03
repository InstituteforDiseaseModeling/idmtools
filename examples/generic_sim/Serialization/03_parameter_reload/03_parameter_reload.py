import os
import sys

sys.path.append('../')

from idmtools.assets import Asset
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.managers import ExperimentManager
from idmtools_model_emod import EMODExperiment
from idmtools_model_emod.generic.serialization import add_serialization_timesteps, load_serialized_population
from globals import *
from analyzers import TimeseriesAnalyzer
from idmtools.analysis.analyze_manager import AnalyzeManager
from idmtools.analysis.download_analyzer import DownloadAnalyzer

SERIALIZATION_PATH = os.path.abspath(os.path.join(current_directory, "01_write_file_singlenode", "outputs"))

try:
    random_sim_id = os.listdir(SERIALIZATION_PATH)[-1]
    SERIALIZATION_PATH = os.path.join(SERIALIZATION_PATH, random_sim_id)
except Exception:
    raise FileNotFoundError("Can't find serialization file from previous run, please make sure 01_write_file_singlenode"
                            " succeeded.")

EXPERIMENT_NAME = 'Generic serialization 03 parameter reload'
SERIALIZATION_FILENAME = "state-00050.dtk"
CHANNELS_TOLERANCE = {'Statistical Population': 1,
                      'Infectious Population': 0.05,
                      'Waning Population': 0.05,
                      'New Infections': 20,
                      'Symptomatic Population': 40}

if __name__ == "__main__":
    # Create the platform
    platform = Platform('COMPS')

    # Create an experiment from input files
    e = EMODExperiment.from_files(EXPERIMENT_NAME, eradication_path=os.path.join(BIN_PATH, "Eradication.exe"),
                                  config_path=os.path.join(INPUT_PATH, 'config.json'),
                                  campaign_path=os.path.join(INPUT_PATH, "campaign.json"),
                                  demographics_paths=os.path.join(INPUT_PATH, "demographics.json"))

    # Add the dtk_file to the asset collection
    dtk_file = Asset(absolute_path=os.path.join(SERIALIZATION_PATH, SERIALIZATION_FILENAME))
    e.add_asset(dtk_file)

    # Retrieve the base_simulation
    simulation = e.base_simulation

    # Change the campaign and various parameters
    simulation.load_files(campaign_path=os.path.join(INPUT_PATH, "campaign.json"))
    config_update_params(simulation)
    simulation.set_parameter("Start_Time", PRE_SERIALIZATION_DAY)
    simulation.set_parameter("Simulation_Duration", SIMULATION_DURATION - PRE_SERIALIZATION_DAY)

    # Enable the serialization and reload the population from the dtk file stored in the assets
    add_serialization_timesteps(simulation=simulation, timesteps=[LAST_SERIALIZATION_DAY],
                                end_at_final=False, use_absolute_times=True)
    load_serialized_population(simulation=simulation, population_path="Assets",
                               population_filenames=[SERIALIZATION_FILENAME])

    # Create the sweep for the repetitions and for the sweep on Base_Infectivity
    e.builder = get_seed_experiment_builder()
    set_Base_Infectivity = partial(param_update, param="Base_Infectivity")
    e.builder.add_sweep_definition(set_Base_Infectivity, [0.2, 1])

    # Experiment manager to run the experiment
    em = ExperimentManager(experiment=e, platform=platform)
    em.run()
    em.wait_till_done()

    if not e.succeeded:
        print(f"Experiment {e.uid} failed.\n")
        exit()

    # Retrieve the parent experiment (The one used to generate the serialized population)
    pre_exp = platform.get_parent(random_sim_id, ItemType.SIMULATION)

    # Analyze
    print(f"Running TimeseriesAnalyzer with experiment id: {e.uid} and {pre_exp.uid}:\n")
    analyzers_timeseries = TimeseriesAnalyzer()
    am_timeseries = AnalyzeManager(platform=platform)
    am_timeseries.add_analyzer(analyzers_timeseries)
    am_timeseries.add_item(e)
    am_timeseries.add_item(pre_exp)
    am_timeseries.analyze()
    analyzers_timeseries.interpret_results(CHANNELS_TOLERANCE)

    # Download the serialization files
    print("Downloading dtk serialization files from Comps:\n")
    filenames = ['output/InsetChart.json', "output/state-" +
                 str(LAST_SERIALIZATION_DAY - PRE_SERIALIZATION_DAY).zfill(5) + ".dtk"]

    # Clean up output path if present
    output_path = 'outputs'
    del_folder(output_path)

    # Download
    analyzers_download = DownloadAnalyzer(filenames=filenames, output_path=output_path)
    am_download = AnalyzeManager(platform=platform)
    am_download.add_analyzer(analyzers_download)
    am_download.add_item(e)
    am_download.analyze()
