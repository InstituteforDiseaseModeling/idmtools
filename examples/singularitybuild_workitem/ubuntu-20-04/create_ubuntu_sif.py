# This script is to create base ubuntu 20.04 singularity container based on the definition file ubuntu_20_04_base.def

from idmtools.core.platform_factory import Platform
from idmtools_platform_comps.utils.singularity_build import SingularityBuildWorkItem

if __name__ == '__main__':
    platform = Platform("CALCULON")
    sbi = SingularityBuildWorkItem(name="Create ubuntu sif with def file", definition_file="ubuntu_20_04_base.def", image_name="ubuntu.sif")
    sbi.tags = dict(ubuntu="20.04")
    sbi.run(wait_until_done=True, platform=platform)
