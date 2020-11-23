from pathlib import PurePath
from idmtools.core.platform_factory import Platform
from idmtools_platform_comps.utils.singularity_build import SingularityBuildWorkItem

if __name__ == "__main__":
    platform = Platform("CALCULON")
    pwd = PurePath(__file__).parent
    ub_base = pwd.joinpath("..", "ubuntu-20-04")
    ubi = SingularityBuildWorkItem(name="Create ubuntu sif with def file", definition_file=ub_base.joinpath("ubuntu_20_04_base.def"), image_name="ubuntu.sif")
    ubi.tags = dict(ubuntu="20.04")
    ubi.run(wait_until_done=True, platform=platform)
    if ubi.succeeded:
        ubi.asset_collection.to_id_file(pwd.joinpath("ubuntu.id"))
