import sys

from analyzers import TimeseriesAnalyzer

sys.path.append('../')

from idmtools.assets import Asset
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.managers import ExperimentManager
from idmtools_model_emod import EMODExperiment
from idmtools_model_emod.generic.serialization import load_serialized_population, add_serialization_timesteps
from idmtools.analysis.AnalyzeManager import AnalyzeManager
from idmtools.analysis.DownloadAnalyzer import DownloadAnalyzer
from globals import *

EXPERIMENT_NAME = 'Generic serialization 02 read files'
DTK_SERIALIZATION_FILENAME = "state-00050.dtk"
CHANNELS_TOLERANCE = {'Statistical Population': 1,
                      'Infectious Population': 0.05,
                      'Waning Population': 0.05,
                      'New Infections': 100,
                      'Symptomatic Population': 200}

if __name__ == "__main__":
    # Create the platform
    platform = Platform('COMPS-Linux')

    # Create the experiment by providing the input files
    e = EMODExperiment.from_files(EXPERIMENT_NAME, eradication_path=os.path.join(BIN_PATH, "Eradication"),
                                  config_path=os.path.join(INPUT_PATH, 'config.json'),
                                  campaign_path=os.path.join(INPUT_PATH, "campaign.json"),
                                  demographics_paths=os.path.join(INPUT_PATH, "demographics.json"))

    # Add the serialized population file to the experiment
    e.add_asset(Asset(absolute_path=os.path.join(SERIALIZATION_PATH, DTK_SERIALIZATION_FILENAME)))

    # Set parameters in the base simulation
    simulation = e.base_simulation
    # Serialization parameters: Enable serialization and reload the population
    add_serialization_timesteps(simulation=simulation, timesteps=[LAST_SERIALIZATION_DAY],
                                end_at_final=False, use_absolute_times=True)
    load_serialized_population(simulation=simulation, population_path="Assets",
                               population_filenames=[DTK_SERIALIZATION_FILENAME])
    # Configuration parameters
    config_update_params(simulation)
    simulation.set_parameter("Start_Time", PRE_SERIALIZATION_DAY)
    simulation.set_parameter("Simulation_Duration", SIMULATION_DURATION - PRE_SERIALIZATION_DAY)

    # Create the sweep on seed
    builder = ExperimentBuilder()
    set_Run_Number = partial(param_update, param="Run_Number")
    builder.add_sweep_definition(set_Run_Number, range(REPETITIONS))
    e.add_builder(builder)

    # Create the experiment manager and run
    em = ExperimentManager(experiment=e, platform=platform)
    em.run()
    em.wait_till_done()

    if e.succeeded:
        print(f"Experiment {e.uid} succeeded.\n")

        # Retrieve the experiment that was used to create the serialization
        pre_exp = platform.get_parent(random_sim_id, ItemType.SIMULATION)

        # Configure the analyzer to work on the InsetChart.json
        analyzers_timeseries = TimeseriesAnalyzer()

        # Create the analyze manager and analyze
        print(f"Running TimeseriesAnalyzer with experiment id: {e.uid} and {pre_exp.uid}:\n")
        am_timeseries = AnalyzeManager(platform=platform)
        am_timeseries.add_analyzer(analyzers_timeseries)
        am_timeseries.add_item(e)
        am_timeseries.add_item(pre_exp)
        am_timeseries.analyze()

        # Interpret results
        analyzers_timeseries.interpret_results(tolerances=CHANNELS_TOLERANCE)

        # Download the serialization files from COMPS
        print("Downloading dtk serialization files from Comps:\n")
        filenames = ['output/InsetChart.json',
                     "output/state-" + str(LAST_SERIALIZATION_DAY - PRE_SERIALIZATION_DAY).zfill(5) + ".dtk"]

        # Clean up previously ran analyzers if any
        output_path = 'outputs'
        if os.path.exists(output_path):
            del_folder(output_path)

        # Run the analysis
        analyzer_download = DownloadAnalyzer(filenames=filenames, output_path=output_path)
        am_download = AnalyzeManager(platform=platform)
        am_download.add_item(e)
        am_download.add_analyzer(analyzer_download)
        am_download.analyze()

    else:
        print(f"Experiment {e.uid} failed.\n")
