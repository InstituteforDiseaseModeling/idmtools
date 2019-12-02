import sys

sys.path.append('../')
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.managers import ExperimentManager
from idmtools_model_emod import EMODExperiment
from idmtools_model_emod.generic.serialization import add_serialization_timesteps, load_serialized_population
from idmtools.utils.filters.asset_filters import file_name_is
from analyzers import TimeseriesAnalyzer
from idmtools.analysis.analyze_manager import AnalyzeManager
from idmtools.analysis.download_analyzer import DownloadAnalyzer

from globals import *


MULTICORE_SERIALIZATION_PATH = os.path.abspath(os.path.join(current_directory, "06_write_file_multicore", "outputs"))
try:
    multicore_random_sim_id = os.listdir(MULTICORE_SERIALIZATION_PATH)[-1]
    MULTICORE_SERIALIZATION_PATH = os.path.join(MULTICORE_SERIALIZATION_PATH, multicore_random_sim_id)
except Exception:
    raise FileNotFoundError("Can't find serialization file from previous run, please make sure 06_write_file_multicore"
                            " succeeded.")

EXPERIMENT_NAME = 'Generic serialization 07 read files multicore'
DTK_SERIALIZATION_FILENAMES = [f"state-00050-{str(i).zfill(3)}.dtk" for i in range(NUM_CORES)]
CHANNELS_TOLERANCE = {'Statistical Population': 1,
                      'Infectious Population': 0.05,
                      'Waning Population': 0.05,
                      'New Infections': 100,
                      'Symptomatic Population': 200}

if __name__ == "__main__":
    # Create the platform
    platform = Platform('COMPS-Multicore')

    # Create an experiment with input files
    e = EMODExperiment.from_files(EXPERIMENT_NAME, eradication_path=os.path.join(BIN_PATH, "Eradication.exe"),
                                  config_path=os.path.join(INPUT_PATH, 'config.json'),
                                  campaign_path=os.path.join(INPUT_PATH, "campaign.json"),
                                  demographics_paths=os.path.join(INPUT_PATH, "9nodes_demographics.json"))

    # Add the serialization filenames to the experiment collection
    filter_name = partial(file_name_is, filenames=DTK_SERIALIZATION_FILENAMES)
    e.assets.add_directory(assets_directory=MULTICORE_SERIALIZATION_PATH, filters=[filter_name])

    # Retrieve the base simulation
    simulation = e.base_simulation

    # Update parameters and setup serialization
    config_update_params(simulation)
    add_serialization_timesteps(simulation=simulation, timesteps=[LAST_SERIALIZATION_DAY],
                                end_at_final=False, use_absolute_times=True)
    load_serialized_population(simulation=simulation, population_path="Assets",
                               population_filenames=DTK_SERIALIZATION_FILENAMES)
    simulation.update_parameters({
        "Start_Time": PRE_SERIALIZATION_DAY,
        "Simulation_Duration": SIMULATION_DURATION - PRE_SERIALIZATION_DAY,
        "Num_Cores": NUM_CORES})

    # Retrieve the sweep on seed
    builder = get_seed_experiment_builder()
    e.add_builder(builder)

    # Create the experiment manager and run
    em = ExperimentManager(experiment=e, platform=platform)
    em.run()
    em.wait_till_done()

    if not e.succeeded:
        print(f"Experiment {e.uid} failed.\n")
        exit()

    # Retrieve the experiment used to generate the serialized population
    pre_exp = platform.get_parent(multicore_random_sim_id, ItemType.SIMULATION)

    # Run the timeseries analyzer
    print(f"Running TimeseriesAnalyzer with experiment id: {e.uid} and {pre_exp.uid}:\n")
    analyzers_timeseries = TimeseriesAnalyzer()
    am_timeseries = AnalyzeManager(platform=platform)
    am_timeseries.add_analyzer(analyzers_timeseries)
    am_timeseries.add_item(e)
    am_timeseries.add_item(pre_exp)
    am_timeseries.analyze()

    analyzers_timeseries.interpret_results(CHANNELS_TOLERANCE)

    # Download the  serialization files
    print("Downloading dtk serialization files from Comps:\n")
    filenames = ['output/InsetChart.json']
    for i in range(4):
        filenames.append(
            f"output/state-{str(LAST_SERIALIZATION_DAY - PRE_SERIALIZATION_DAY).zfill(5)}-{str(i).zfill(3)}.dtk")

    # Delete outputs if present
    output_path = 'outputs'
    del_folder(output_path)

    # Download
    analyzers_download = DownloadAnalyzer(filenames=filenames, output_path=output_path)
    am_download = AnalyzeManager(platform=platform)
    am_download.add_analyzer(analyzers_download)
    am_download.add_item(e)
    am_download.analyze()
