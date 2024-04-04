import os
import sys
from idmtools.assets import AssetCollection
from idmtools.core.platform_factory import Platform
from idmtools_platform_comps.ssmt_work_items.comps_workitems import SSMTWorkItem

# run command in comps's workitem
command = "python3 Assets/analyzer_file.py"
# load everything including analyzers from local 'analyzers' dir to comps's Assets dir in workitem

if __name__ == "__main__":
    platform = Platform('CALCULON')
    wi = SSMTWorkItem(name=os.path.split(sys.argv[0])[1], command=command, assets=AssetCollection.from_directory("analyzers"))

    wi.run(True, platform=platform)
