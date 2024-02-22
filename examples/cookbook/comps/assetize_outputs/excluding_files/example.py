from idmtools.core.platform_factory import Platform
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
from idmtools_platform_comps.utils.assetize_output.assetize_output import AssetizeOutput

task = CommandTask(command="python Assets/model.py")
task.common_assets.add_asset("model.py")

platform = Platform("BELEGOST")
experiment = Experiment.from_task(task)

# Since we have one simulation in our experiment, we can "flatten output" by using the format str
ao = AssetizeOutput(file_patterns=["*.out"], related_experiments=[experiment], no_simulation_prefix=True)
# Exclude some output files while preserving the default exclusions of stdout and stderr.txt
ao.exclude_patterns.append("3.out")
ao.exclude_patterns.append("5.out")
ao.run(wait_until_done=True)

if ao.succeeded:
    for asset in sorted(ao.asset_collection, key=lambda sa: sa.short_remote_path().rjust(6)):
        print(asset.short_remote_path().rjust(6))
else:
    print('Item failed. Check item output')
