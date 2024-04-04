from idmtools.assets import AssetCollection
from idmtools.core.platform_factory import Platform
from idmtools_platform_comps.ssmt_work_items.comps_workitems import SSMTWorkItem

wi_name = "SSMT Analysis generic 1"
command = "python3 run_analysis.py"

if __name__ == "__main__":
    platform = Platform('CALCULON')
    wi = SSMTWorkItem(name=wi_name, command=command, transient_assets=AssetCollection.from_directory('files'), related_experiments=["b716f387-cb04-eb11-a2c7-c4346bcb1553"])  # COMPS exp_id
    wi.run(wait_until_done=True)
