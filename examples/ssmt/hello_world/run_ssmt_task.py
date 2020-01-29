from idmtools.assets.FileList import FileList
from idmtools.core.platform_factory import Platform
from idmtools.managers.work_item_manager import WorkItemManager
from idmtools.ssmt.ssmt_work_item import SSMTWorkItem

wi_name = "SSMT Hello 1"
command = "python hello.py"
user_files = FileList(root='files')
tags = {'test': 123}

if __name__ == "__main__":
    platform = Platform('COMPS2')
    wi = SSMTWorkItem(item_name=wi_name, command=command, user_files=user_files, tags=tags)
    wim = WorkItemManager(wi, platform)
    wim.process(check_status=True)
