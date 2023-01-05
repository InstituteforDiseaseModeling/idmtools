# this example creates 2 experiments/simulations and python versions show in stdout.txt file in each simulation
import os.path

from idmtools.assets import AssetCollection
from idmtools.core.platform_factory import Platform
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment


def check_versions():
    command = "singularity exec ./Assets/dtk_run_rocky_py39.sif pip3 list"
    task = CommandTask(command=command)
    #task.common_assets.add_asset(os.path.join("asset", "EMOD_ENV_almalinux8.sif"))
    task.common_assets.add_assets(AssetCollection.from_id("c94763e4-8f55-ed11-a9ff-b88303911bc1"))

    experiment = Experiment.from_task(
        task,
        name="singularity pip3 list",
        tags=dict(type='singularity', description='pip3 list')
    )
    return experiment


if __name__ == '__main__':
    platform = Platform('Calculon')
    exp = check_versions()
    exp.run(wait_until_done=True)
