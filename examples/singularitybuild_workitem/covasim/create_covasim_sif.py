# This script creates covasim singularity container named as convasim_ubuntu.sif.
# It is derived from  pre-created ubuntu container with AssetCollection ID as 1694dda9-3f2a-eb11-a2dd-c4346bcb7271
# then added the idm covasim from github repo to this container. the definition file is in covasim_req.def
import os
from pathlib import PurePath

from idmtools.assets import AssetCollection
from idmtools.core.platform_factory import Platform
from idmtools_platform_comps.utils.singularity_build import SingularityBuildWorkItem

if __name__ == '__main__':
    platform = Platform("CALCULON")
    sbi = SingularityBuildWorkItem(name="Create covasim sif with def file", definition_file="covasim_req.def", image_name="covasim_ubuntu.sif")
    # Try to load the ubuntu image from an id file
    pwd = PurePath(__file__).parent
    ub_base = pwd.joinpath("..", "ubuntu-20-04")
    fp = pwd.joinpath("ubuntu.id")
    if os.path.exists(fp):
        sbi.add_assets(AssetCollection.from_id_file(fp))
    else:
        # or attempt build before hand
        ubi = SingularityBuildWorkItem(name="Create ubuntu sif with def file", definition_file=ub_base.joinpath("ubuntu_20_04_base.def"), image_name="ubuntu.sif")
        ubi.tags = dict(ubuntu="20.04")
        ubi.run(wait_until_done=True, platform=platform)
        ubi.asset_collection.to_id_file(fp)
        sbi.add_assets(ubi.asset_collection)
    sbi.tags = dict(covasim=None)
    sbi.run(wait_until_done=True, platform=platform)
    if sbi.succeeded:
        sbi.asset_collection.to_id_file("covasim.id")
