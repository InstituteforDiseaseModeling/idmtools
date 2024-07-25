# This example demonstrates how to run a model that requires additional packages to be installed in the container.
import os
import sys
from idmtools.assets import Asset, AssetCollection
from idmtools.core.platform_factory import Platform
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment


def run_with_extra_packages():
    platform = Platform("Container", job_directory="DEST", new_container=True, extra_packages=['astor'])
    command = "python Assets/model_file.py"
    task = CommandTask(command=command)

    model_asset = Asset(absolute_path=os.path.join("inputs", "extra_packages", "model_file.py"))
    common_assets = AssetCollection()
    common_assets.add_asset(model_asset)
    # create experiment from task
    experiment = Experiment.from_task(task, name="run_with_extra_packages", assets=common_assets)
    experiment.run(wait_until_done=True, platform=platform)
    sys.exit(0 if experiment.succeeded else -1)


if __name__ == '__main__':
    run_with_extra_packages()
