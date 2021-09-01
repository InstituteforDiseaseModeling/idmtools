# Example to download files to local from COMPS with DownloadWorkItem
# You can also run download files with idmtools cli command under current dir
# idmtools comps CALCULON  download --experiment 7a7b7c10-f1f3-eb11-a9ed-b88303911bc1 --name example_test --output-path output_dir --pattern output\** --no-delete-after-download --extract-after-download

import os
import sys

from idmtools_core.idmtools.core.platform_factory import Platform
from idmtools_platform_comps.utils.download.download import DownloadWorkItem

platform = Platform("CALCULON")
cwd = os.getcwd()
os.makedirs(os.path.join(cwd, "output_dir"), exist_ok=True)
dl_wi = DownloadWorkItem(name=os.path.split(sys.argv[0])[1],
                         related_experiments=['7a7b7c10-f1f3-eb11-a9ed-b88303911bc1'],
                         file_patterns=["output/**"], delete_after_download=False,
                         simulation_prefix_format_str='{simulation.id}', verbose=True,
                         output_path=os.path.join(cwd, "output_dir"),
                         )
dl_wi.run(wait_on_done=True, platform=platform)