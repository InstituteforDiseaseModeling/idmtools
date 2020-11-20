import os
import sys

from idmtools.assets import AssetCollection
from idmtools.core.platform_factory import Platform
from idmtools.entities import CommandLine
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
from idmtools.entities.templated_simulation import TemplatedSimulations

if __name__ == "__main__":
    here = os.path.dirname(__file__)

    # Create a platform to run the workitem
    platform = Platform("CALCULON")

    # create commandline input for the task
    command = CommandLine("singularity exec ./Assets/covasim_ubuntu.sif python3 Assets/run_sim.py")
    task = CommandTask(command=command)
    # Add our image
    task.common_assets.add_assets(AssetCollection.from_id_file("covasim.id"))

    experiment = Experiment.from_task(
        task,
        name=os.path.split(sys.argv[0])[1],
        tags=dict(type='singularity', description='run covasim')
    )
    experiment.add_asset(os.path.join("inputs", "run_sim.py"))
    experiment.run(wait_until_done=True)
    if experiment.succeeded:
        experiment.to_id_file("run_sim.id")
