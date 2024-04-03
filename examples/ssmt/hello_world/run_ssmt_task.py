from idmtools.assets import AssetCollection
from idmtools.core.platform_factory import Platform
from idmtools_platform_comps.ssmt_work_items.comps_workitems import SSMTWorkItem

wi_name = "SSMT Hello 1"
command = "python3 hello.py"
tags = {'test': 123}

if __name__ == "__main__":
    with Platform('CALCULON'):

        # If docker_image is defined within idmtools.ini, it It will use this docker image.
        # If docker_image is not defined in idmtools.ini, it will use the default docker image based on platform:
        # 'COMPS' case uses production docker image and 'COMPS' case (and all others) uses the staging docker image.
        wi = SSMTWorkItem(name=wi_name, command=command, transient_assets=AssetCollection.from_directory("files"), tags=tags)

        # Or user can use his won docker image like this
        # wi = SSMTWorkItem(name=wi_name, command=command, transient_assets=user_files, tags=tags, docker_image='User_docker_image')

        wi.run(wait_until_done=True)
