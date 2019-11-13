import sys

sys.path.append('../')

from idmtools.core.platform_factory import Platform
from idmtools.managers import ExperimentManager
from idmtools_model_emod import EMODExperiment
from idmtools_model_emod.generic.serialization import add_serialization_timesteps
from idmtools.analysis.analyze_manager import AnalyzeManager
from idmtools.analysis.download_analyzer import DownloadAnalyzer
from idmtools_model_emod.emod_file import MigrationTypes

from globals import *

EXPERIMENT_NAME = 'Generic serialization 08 writes files migration'
DTK_MIGRATION_FILENAME = "LocalMigration_3_Nodes.bin"
REPETITIONS = 1 # run with only one run_number in this test


if __name__ == "__main__":

    # Create the platform
    platform = Platform('COMPS')

    # Create an experiment based on input files
    e = EMODExperiment.from_files(EXPERIMENT_NAME, eradication_path=os.path.join(BIN_PATH, "Eradication.exe"),
                                  config_path=os.path.join(INPUT_PATH, 'config.json'),
                                  campaign_path=os.path.join(INPUT_PATH, "campaign.json"),
                                  demographics_paths=os.path.join(INPUT_PATH, "3nodes_demographics.json"))

    # Add the migration files
    e.migrations.add_migration_from_file(MigrationTypes.LOCAL, os.path.join(INPUT_PATH, DTK_MIGRATION_FILENAME))

    # Add the DLLs to the collection
    e.dlls.add_dll_folder("../custom_reports/reporter_plugins/Windows")
    e.dlls.set_custom_reports_file("../custom_reports/custom_reports.json")

    # Get the base simulation
    simulation = e.base_simulation

    # Update parameters (adding migration) and setup serialization
    config_update_params(simulation)
    serialization_timesteps = list(range(10, LAST_SERIALIZATION_DAY + 20, 20))
    add_serialization_timesteps(simulation=simulation, timesteps=serialization_timesteps,
                                end_at_final=False, use_absolute_times=False)
    simulation.update_parameters({
        "Start_Time": START_DAY,
        "Simulation_Duration": SIMULATION_DURATION,
        "Enable_Migration_Heterogeneity": 0,
        "Migration_Model": "FIXED_RATE_MIGRATION",
        "Migration_Pattern": "RANDOM_WALK_DIFFUSION",
        "x_Local_Migration": 0.1,
    })

    # Retrieve the seed sweep
    builder = get_seed_experiment_builder(REPETITIONS)
    e.add_builder(builder)

    # Create experiment manager and run
    em = ExperimentManager(experiment=e, platform=platform)
    em.run()
    em.wait_till_done()

    if e.succeeded:
        print(f"Experiment {e.uid} succeeded.\nDownloading dtk serialization files from Comps:\n")

        # Create the filenames
        filenames = ['output/InsetChart.json',
                     'output/ReportHumanMigrationTracking.csv',
                     'output/ReportNodeDemographics.csv']
        for serialization_timestep in serialization_timesteps:
            filenames.append("output/state-" + str(serialization_timestep).zfill(5) + ".dtk")

        # Remove the outputs if already present
        output_path = 'outputs'
        del_folder(output_path)

        download_analyzer = DownloadAnalyzer(filenames=filenames, output_path=output_path)
        am = AnalyzeManager(platform=platform)
        am.add_analyzer(download_analyzer)
        am.add_item(e)
        am.analyze()
    else:
        print(f"Experiment {e.uid} failed.\n")