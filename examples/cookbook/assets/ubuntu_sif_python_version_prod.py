import os

from idmtools.assets import AssetCollection
from idmtools.core.platform_factory import Platform
from idmtools.entities import CommandLine
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment

with Platform("Calculon", priority="highest") as platform:
    sif_id ="319a8051-b733-f111-92e2-000d3af5294c"
    sif_name = "emod-ubuntu-runtime_latest.sif"
    # option code to keep ac in system
    # command = CommandLine(f"singularity exec ./Assets/{sif_name} python --version")
    command = CommandLine(f"singularity exec ./Assets/{sif_name} python3 --version")
    task = CommandTask(command=command)
    common_assets = AssetCollection.from_id(sif_id)
    task.common_assets.add_assets(common_assets)
    experiment = Experiment.from_task(
        task,
        name=os.path.basename(__file__),
        tags=dict(type='singularity', description='run test', sif_ac=sif_id)
    )
    experiment.run(wait_until_done=True)
