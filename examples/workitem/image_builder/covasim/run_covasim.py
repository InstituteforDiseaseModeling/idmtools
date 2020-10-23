import os
import sys

from idmtools.analysis.analyze_manager import AnalyzeManager
from idmtools.analysis.download_analyzer import DownloadAnalyzer
from idmtools.assets import AssetCollection, Asset
from idmtools.core.platform_factory import Platform
from idmtools.entities import CommandLine
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment

# Run a Covasim simulation script on the SLURM cluster
#   This is the most basic implementation and does not use
#   Covasim's built in multi-run simulation manager since core management
#   is handled by the cluster.
#
#   To see an example of running a model with parameter sweeps,
#   please see examples/python_model/python_sim_slurm.py

if __name__ == "__main__":
    here = os.path.dirname(__file__)

    # Create a platform to run the workitem
    platform = Platform("SLURM2")  # staging SLURMStage

    # create commandline input for the task
    command = CommandLine("singularity exec ./Assets/covasim.sif python3 sim.py")
    task = CommandTask(command=command)
    # add required file at top level (sim) dir
    task.transient_assets.add_asset(os.path.join("inputs", "sim.py"))

    # add covasim.sif's assetcollection to experiment level(Assets dir)
    # 0cfbc30b-920d-eb11-a2c2-f0921c167862 assetcollection id in stage which created from create_covasim_sif_ac.py
    common_assets = AssetCollection.from_id("0cfbc30b-920d-eb11-a2c2-f0921c167862", as_copy=True)
    task.common_assets = common_assets

    # create Experiment from task
    experiment = Experiment.from_task(task,
                                      name=os.path.split(sys.argv[0])[1],
                                      tags={
                                          'type': 'singularity',
                                          'description': 'run with exec'
                                      })
    experiment.run(wait_until_done=True)

    # Exit if the experiment fails
    if not experiment.succeeded:
        print(f"Experiment {experiment.uid} failed.\n")
        sys.exit(-1)

    # Download its outputs
    outputs = ["outputs/results.json", "outputs/results.xlsx", "outputs/plot.png"]
    analyzer = DownloadAnalyzer(filenames=outputs, output_path="outputs")
    am = AnalyzeManager(platform=platform, analyzers=[analyzer])
    am.add_item(experiment)
    am.analyze()
