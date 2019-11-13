import sys

sys.path.append('../')

from idmtools.core.platform_factory import Platform
from idmtools.managers import ExperimentManager
from idmtools_model_emod import EMODExperiment
from idmtools_model_emod.defaults import EMODSir
from idmtools_model_emod.generic.serialization import add_serialization_timesteps
from idmtools.analysis.analyze_manager import AnalyzeManager
from idmtools.analysis.download_analyzer import DownloadAnalyzer
from globals import *

EXPERIMENT_NAME = 'Generic serialization 01 writes files'

if __name__ == "__main__":
    # Create the platform
    platform = Platform('COMPS')

    # Experiment from the EMODSIR defaults
    e = EMODExperiment.from_default(EXPERIMENT_NAME, default=EMODSir,
                                    eradication_path=os.path.join(BIN_PATH, "Eradication.exe"))

    # Get the base simulation and set the campaign and demographics
    simulation = e.base_simulation
    simulation.load_files(campaign_path=os.path.join(INPUT_PATH, "campaign.json"))
    e.demographics.clear()
    e.demographics.add_demographics_from_file(os.path.join(INPUT_PATH, "demographics.json"))

    # Update bunch of config parameters
    config_update_params(simulation)

    # Create the serialization timesteps
    serialization_timesteps = list(range(10, LAST_SERIALIZATION_DAY + 20, 20))
    add_serialization_timesteps(simulation=simulation, timesteps=serialization_timesteps,
                                end_at_final=False, use_absolute_times=False)

    # Handle start day and duration
    simulation.set_parameter("Start_Time", START_DAY)
    simulation.set_parameter("Simulation_Duration", SIMULATION_DURATION)

    # Create the sweep for the seed
    builder = get_seed_experiment_builder()

    # Create the manager and run
    em = ExperimentManager(experiment=e, platform=platform)
    em.run()
    em.wait_till_done()

    if e.succeeded:
        print(f"Experiment {e.uid} succeeded.\nDownloading dtk serialization files from Comps:\n")

        # Cleanup the output path
        output_path = 'outputs'
        if os.path.exists(output_path):
            del_folder(output_path)

        # We want to download all the dtk state files and the InsetChart.json
        filenames = []
        for serialization_timestep in serialization_timesteps:
            filenames.append("output/state-" + str(serialization_timestep).zfill(5) + ".dtk")
        filenames.append('output/InsetChart.json')

        # Create the analyze manager
        am = AnalyzeManager(platform=platform)
        am.add_item(e)
        am.add_analyzer(DownloadAnalyzer(filenames=filenames, output_path=output_path))

        # Analyze
        am.analyze()
    else:
        print(f"Experiment {e.uid} failed.\n")
