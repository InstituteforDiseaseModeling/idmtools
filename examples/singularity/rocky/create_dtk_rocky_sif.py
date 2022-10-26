# This script is to create base ubuntu 20.04 singularity container based on the definition file ubuntu_20_04_base.def
import os
import sys

from idmtools.core.platform_factory import Platform
from idmtools_platform_comps.utils.download.download import DownloadWorkItem
from idmtools_platform_comps.utils.singularity_build import SingularityBuildWorkItem

if __name__ == '__main__':
    platform = Platform("CALCULON")
    sbi = SingularityBuildWorkItem(name="Create dtk rocky sif", definition_file="dtk_build_rocky.def", image_name="dtk_build_rocky_39.sif", force=True)
    sbi.tags = dict(python="3.9")
    sbi.run(wait_until_done=True, platform=platform)
    if sbi.succeeded:
        # Write ID file
        sbi.asset_collection.to_id_file("dtk_rock_prod.id")

        dl_wi = DownloadWorkItem(name="download sif file",
                                 related_work_items=[sbi.id],
                                 file_patterns=["dtk_build_rocky_39.sif"], delete_after_download=False,
                                 verbose=True,
                                 output_path=os.path.join(os.getcwd(), "output_sif"),
                                 )
        dl_wi.run(wait_on_done=True, platform=platform)
