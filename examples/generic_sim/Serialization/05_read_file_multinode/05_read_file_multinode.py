import sys

from analyzers import TimeseriesAnalyzer

sys.path.append('../')
from idmtools.assets import Asset
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.managers import ExperimentManager
from idmtools_model_emod import EMODExperiment
from idmtools_model_emod.generic.serialization import add_serialization_timesteps, load_serialized_population
from idmtools.analysis.AnalyzeManager import AnalyzeManager
from idmtools.analysis.DownloadAnalyzer import DownloadAnalyzer
from globals import *

EXPERIMENT_NAME = 'Generic serialization 05 read files multinode'
DTK_SERIALIZATION_FILENAME = "state-00050.dtk"
CHANNELS_TOLERANCE = {'Statistical Population': 1,
                      'Infectious Population': 0.05,
                      'Waning Population': 0.05,
                      'New Infections': 100,
                      'Symptomatic Population': 200}

if __name__ == "__main__":
    # Create the platform
    platform = Platform('COMPS')

    # Create an experiment based on input files
    e = EMODExperiment.from_files(EXPERIMENT_NAME, eradication_path=os.path.join(BIN_PATH, "Eradication.exe"),
                                  config_path=os.path.join(INPUT_PATH, 'config.json'),
                                  campaign_path=os.path.join(INPUT_PATH, "campaign.json"),
                                  demographics_paths=os.path.join(INPUT_PATH, "9nodes_demographics.json"))

    # Add the serialized population to the experiment's assets
    dtk_file = Asset(absolute_path=os.path.join(MULTINODE_SERIALIZATION_PATH, DTK_SERIALIZATION_FILENAME))
    e.add_asset(dtk_file)

    # Retrieve the base simulation
    simulation = e.base_simulation

    # UUpdate config parameters and configure serialization
    config_update_params(simulation)
    simulation.update_parameters({
        "Start_Time": PRE_SERIALIZATION_DAY,
        "Simulation_Duration": SIMULATION_DURATION - PRE_SERIALIZATION_DAY})
    add_serialization_timesteps(simulation=simulation, timesteps=[LAST_SERIALIZATION_DAY],
                                end_at_final=False, use_absolute_times=True)
    load_serialized_population(simulation=simulation, population_path="Assets",
                               population_filenames=[DTK_SERIALIZATION_FILENAME])

    # Add the seeds builder
    builder = get_seed_experiment_builder()
    e.add_builder(builder)

    # Create the experiment manager and run
    em = ExperimentManager(experiment=e, platform=platform)
    em.run()
    em.wait_till_done()

    if e.succeeded:
        print(f"Experiment {e.uid} succeeded.\n")

        # Get the parent experiment (used to generate the serialized population)
        pre_exp = platform.get_parent(multinode_random_sim_id, ItemType.SIMULATION)

        print(f"Running TimeseriesAnalyzer with experiment id: {e.uid} and {pre_exp.uid}:\n")

        analyzers_timeseries = TimeseriesAnalyzer()
        am_timeseries = AnalyzeManager(platform=platform)
        am_timeseries.add_analyzer(analyzers_timeseries)
        am_timeseries.add_item(e)
        am_timeseries.add_item(pre_exp)
        am_timeseries.analyze()

        analyzers_timeseries.interpret_results(CHANNELS_TOLERANCE)

        # Download the dtk serialization files
        print("Downloading dtk serialization files from Comps:\n")
        filenames = ['output/InsetChart.json', "output/state-" +
                     str(LAST_SERIALIZATION_DAY - PRE_SERIALIZATION_DAY).zfill(5) + ".dtk"]

        # Cleanup if the outputs already exist
        output_path = 'outputs'
        if os.path.exists(output_path):
            del_folder(output_path)

        analyzers_download = DownloadAnalyzer(filenames=filenames, output_path=output_path)
        am_download = AnalyzeManager(platform=platform)
        am_download.add_analyzer(analyzers_download)
        am_download.add_item(e)
        am_download.analyze()

    else:
        print(f"Experiment {e.uid} failed.\n")
