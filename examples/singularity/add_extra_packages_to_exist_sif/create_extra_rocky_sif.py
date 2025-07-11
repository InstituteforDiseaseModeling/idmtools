# This script creates sif image with extra packages added to the existing rocky sif image.
from idmtools.assets import AssetCollection
from idmtools.core.platform_factory import Platform
from idmtools_platform_comps.utils.singularity_build import SingularityBuildWorkItem

if __name__ == '__main__':
    platform = Platform("CALCULON")
    sbi = SingularityBuildWorkItem(name="Create extra package for rocky", definition_file="rocky_runner_added.def", image_name="rocky_runner_extra.sif")
    # Add existing sif id file to asset
    sbi.add_assets(AssetCollection.from_id_file("rocky_dtk_runner_py39.sif.id"))
    sbi.tags = dict(rocky_extra=None)
    ac = sbi.run(wait_until_done=True, platform=platform)
    if sbi.succeeded:
        ac.to_id_file("rocky_runner_extra.sif.id")
