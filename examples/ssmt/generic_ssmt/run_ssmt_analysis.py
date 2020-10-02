from idmtools.assets.file_list import FileList
from idmtools.core.platform_factory import Platform
from idmtools_platform_comps.ssmt_work_items.comps_workitems import SSMTWorkItem

wi_name = "SSMT Analysis generic 1"
command = "python run_analysis.py"
user_files = FileList(root='files')

if __name__ == "__main__":
    platform = Platform('BELEGOST')
    wi = SSMTWorkItem(item_name=wi_name, command=command, user_files=user_files,
                      related_experiments=["b716f387-cb04-eb11-a2c7-c4346bcb1553"])  # COMPS exp_id
    wi.run(wait_on_done=True)
