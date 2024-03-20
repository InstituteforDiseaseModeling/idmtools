# This script is to create base ubuntu 20.04 singularity container based on the definition file ubuntu_20_04_base.def
import os
import sys

from COMPS.utils.get_output_files_for_workitem import get_files

from idmtools.core.platform_factory import Platform
from idmtools_platform_comps.utils.singularity_build import SingularityBuildWorkItem

if __name__ == '__main__':
    platform = Platform("Calculon")
    sbi = SingularityBuildWorkItem(name="Create dtk rocky sif", definition_file="dtk_run_rocky_py39.def", image_name="dtk_run_rocky_py39.sif", force=True)
    sbi.tags = {"python": "3.9", "rockylinux": "8.5"}
    ac_obj = sbi.run(wait_until_done=True, platform=platform)

    if sbi.succeeded:
        print("sbi.id: ", sbi.id)
        # Write ID file
        ac_obj.to_id_file(f"{platform._config_block}_dtk_run_rocky_py39_prod.id")
        print("ac_obj: ", ac_obj.id)
        # uncomment the following line to download dtk_run_rocky_py39.sif to local current directory
        #get_files(sbi.id, "dtk_run_rocky_py39.sif")