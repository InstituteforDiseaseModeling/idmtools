from idmtools.assets.file_list import FileList
from idmtools.core.platform_factory import Platform
from idmtools_platform_comps.ssmt_work_items.comps_workitems import SSMTWorkItem

wi_name = "SSMT Hello 1"
command = "python hello.py"
user_files = FileList(root='files')
tags = {'test': 123}

if __name__ == "__main__":
    platform = Platform('COMPS2')
    wi = SSMTWorkItem(item_name=wi_name, command=command, user_files=user_files, tags=tags)
    platform.run_items(wi)
    platform.wait_till_done(wi)
