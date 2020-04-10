from idmtools.assets.file_list import FileList
from idmtools.core.platform_factory import Platform
from idmtools_platform_comps.ssmt_work_items.comps_workitems import SSMTWorkItem

wi_name = "SSMT Hello 1"
command = "python hello.py"
user_files = FileList(root='files')
tags = {'test': 123}

if __name__ == "__main__":
    platform = Platform('COMPS2')

    # It will use docker image if docker_image is defined in idmtools.ini
    # If docker_image is not defined in idmtools.ini, it will use the default docker image based on platform
    # 'COMPS' case uses production docker image and 'COMPS2' case uses the staging docker image
    wi = SSMTWorkItem(item_name=wi_name, command=command, user_files=user_files, tags=tags)

    # Or user can use his won docker image like this
    # wi = SSMTWorkItem(item_name=wi_name, command=command, user_files=user_files, tags=tags,
    #                   docker_image='User_docker_image')

    platform.run_items(wi)
    platform.wait_till_done(wi)
