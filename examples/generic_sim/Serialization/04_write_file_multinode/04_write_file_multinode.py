import sys

sys.path.append('../')

from idmtools.core.platform_factory import Platform
from idmtools.managers import ExperimentManager
from idmtools_model_emod import EMODExperiment
from idmtools_model_emod.generic.serialization import add_serialization_timesteps
from idmtools.analysis.analyze_manager import AnalyzeManager
from idmtools.analysis.download_analyzer import DownloadAnalyzer

from globals import *

EXPERIMENT_NAME = 'Generic serialization 04 writes files multinode'
REPETITIONS = 1 # run with only one run_number in this test

if __name__ == "__main__":
    # Create the platform
    platform = Platform('COMPS-Linux')

    # Create the experiment from input files
    e = EMODExperiment.from_files(EXPERIMENT_NAME, eradication_path=os.path.join(BIN_PATH, "Eradication"),
                                  config_path=os.path.join(INPUT_PATH, 'config.json'),
                                  campaign_path=os.path.join(INPUT_PATH, "campaign.json"),
                                  demographics_paths=os.path.join(INPUT_PATH, "9nodes_demographics.json"))

    # Get the base simulation
    simulation = e.base_simulation

    # Update the configuration parameters and enable serialization
    config_update_params(simulation)
    serialization_timesteps = list(range(10, LAST_SERIALIZATION_DAY + 20, 20))
    add_serialization_timesteps(simulation=simulation, timesteps=serialization_timesteps,
                                end_at_final=False, use_absolute_times=False)
    simulation.update_parameters({
        "Start_Time": START_DAY,
        "Simulation_Duration": SIMULATION_DURATION
        # "Random_Number_Generator_Policy": "ONE_PER_NODE",
        # "Random_Number_Generator_Type": "USE_PSEUDO_DES"
    })

    # Create the sweep on seeds
    builder = get_seed_experiment_builder(REPETITIONS)
    e.add_builder(builder)

    # Create the manager and run
    em = ExperimentManager(experiment=e, platform=platform)
    em.run()
    em.wait_till_done()

    if e.succeeded:
        print(f"Experiment {e.uid} succeeded.\nDownloading dtk serialization files from Comps:\n")

        # Create the filename list
        filenames = []
        for serialization_timestep in serialization_timesteps:
            filenames.append("output/state-" + str(serialization_timestep).zfill(5) + ".dtk")
        filenames.append('output/InsetChart.json')

        # Delete the outputs if existed already
        output_path = 'outputs'
        del_folder(output_path)

        # Download the files
        am = AnalyzeManager(platform=platform)
        download_analyzer = DownloadAnalyzer(filenames=filenames, output_path=output_path)
        am.add_analyzer(download_analyzer)
        am.add_item(e)
        am.analyze()
    else:
        print(f"Experiment {e.uid} failed.\n")
