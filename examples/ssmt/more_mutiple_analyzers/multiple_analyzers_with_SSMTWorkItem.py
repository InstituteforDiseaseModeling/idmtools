import os
import sys

from idmtools.assets.file_list import FileList
from idmtools.core.platform_factory import Platform
from idmtools_platform_comps.ssmt_work_items.comps_workitems import SSMTWorkItem

# run command in comps's workitem
command = "python Assets/analyzer_file.py"
# load everything including analyzers from local 'analyzers' dir to comps's Assets dir in workitem
asset_files = FileList(root='analyzers')

# load idmtools.ini to comps2 workitem which is needed for Platform
user_files = FileList()
current_path = os.path.dirname(__file__)
user_files.add_file(os.path.join(current_path, "idmtools.ini"))

if __name__ == "__main__":
    platform = Platform('COMPS2')
    wi = SSMTWorkItem(item_name=os.path.split(sys.argv[0])[1], command=command, asset_files=asset_files, user_files=user_files)

    wi.run(True, platform=platform)

