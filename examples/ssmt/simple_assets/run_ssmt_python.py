from idmtools.assets import AssetCollection
from idmtools.core.platform_factory import Platform
from idmtools_platform_comps.ssmt_work_items.comps_workitems import SSMTWorkItem

wi_name = "SSMT AssetCollection Hello 1"
command = "python3 Assets/Hello_model.py"

if __name__ == "__main__":
    platform = Platform('CALCULON')
    wi = SSMTWorkItem(name=wi_name, command=command, assets=AssetCollection.from_directory("Assets"))
    wi.run(True, platform=platform)

    # user can also run wi with platform as following
    # platform.run_items(wi)
    # platform.wait_till_done(wi)
