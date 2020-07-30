import os
import sys

from idmtools.analysis.analyze_manager import AnalyzeManager
from idmtools.analysis.download_analyzer import DownloadAnalyzer
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
    platform = Platform('SLURM')

    # create commandline input for the task
    command = CommandLine("./Assets/run.sh")
    task = CommandTask(command=command)

    # create Experiment from task
    experiment = Experiment.from_task(task,
                                      name="covasim",
                                      tags={
                                          'type': 'singularity',
                                          'description': 'run with exec'
                                      })
    experiment.assets.add_directory(assets_directory=os.path.join(here, 'inputs'))
    platform.run_items(experiment)
    platform.wait_till_done(experiment)

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
