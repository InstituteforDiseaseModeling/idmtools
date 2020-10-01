from idmtools.assets.file_list import FileList
from idmtools.core.platform_factory import Platform
from idmtools_platform_comps.ssmt_work_items.comps_workitems import SSMTWorkItem

wi_name = "SSMT AssetCollection Hello 1"
command = "python Assets/Hello_model.py"
asset_files = FileList(root='Assets')

if __name__ == "__main__":
    platform = Platform('COMPS')
    wi = SSMTWorkItem(item_name=wi_name, command=command, asset_files=asset_files)
    wi.run(True, platform=platform)

    # user can also run wi with platform as following
    # platform.run_items(wi)
    # platform.wait_till_done(wi)
