# from simtools.Managers.WorkItemManager import WorkItemManager
# from simtools.SetupParser import SetupParser
# from simtools.AssetManager.FileList import FileList
from idmtools.assets.FileList import FileList
from idmtools.core.platform_factory import Platform
from idmtools.managers.work_item_manager import WorkItemManager
from idmtools.ssmt.ssmt_work_item import SSMTWorkItem

wi_name = "SSMT Analysis generic 1"
command = "python run_analysis.py"
user_files = FileList(root='files')

if __name__ == "__main__":
    # import inspect
    # s = inspect.signature(SSMTWorkItem.__init__)
    # print(s)
    # exit()

    platform = Platform('SSMT')
    wi = SSMTWorkItem(item_name=wi_name, command=command, user_files=user_files,
                      related_experiments=["8bb8ae8f-793c-ea11-a2be-f0921c167861"])
    wim = WorkItemManager(wi, platform)
    wim.process(check_status=True)
