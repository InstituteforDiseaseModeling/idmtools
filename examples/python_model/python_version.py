# this example creates 2 experiments/simulations and python versions show in stdout.txt file in each simulation
import sys

from idmtools.assets import AssetCollection, Asset

from idmtools.core.platform_factory import Platform
from idmtools.entities import Suite
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment


def run_python_version():
    command = "python3 --version"
    task = CommandTask(command=command)
    experiment = Experiment.from_task(task, name="run_python_version")
    return experiment


def run_sif_python_version():
    command = "singularity exec ./Assets/dtk_run_rocky_py39.sif python3 --version"
    task = CommandTask(command=command)
    sif_asset_id = "b5db36a4-7ccd-ec11-a9f8-b88303911bc1"  # pre_loaded sif as assetcollection in COMPS
    task.common_assets.add_assets(AssetCollection.from_id(sif_asset_id))

    experiment = Experiment.from_task(
        task,
        name="singularity version",
        tags=dict(type='singularity', description='python version')
    )
    return experiment


if __name__ == '__main__':
    platform = Platform('Calculon')
    suite = Suite(name='python versions')
    platform.create_items([suite])
    exp1 = run_python_version()
    exp2 = run_sif_python_version()
    # add experiment to suite
    suite.add_experiment(exp1)
    suite.add_experiment(exp2)
    exp1.run(wait_until_done=True)
    exp2.run(wait_until_done=True)
    sys.exit(0 if suite.succeeded else -1)