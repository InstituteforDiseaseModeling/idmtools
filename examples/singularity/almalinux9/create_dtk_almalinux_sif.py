from COMPS.utils.get_output_files_for_workitem import get_files

from idmtools.core.platform_factory import Platform
from idmtools_platform_comps.utils.singularity_build import SingularityBuildWorkItem


# Start and experiment on COMPS
def make_work():

  # Prepare the platform
  platform = Platform('Calculon')

  # Creates a single work item to create the image
  sbwi= SingularityBuildWorkItem(name='Build_EMOD_ENV_39',
                                 definition_file='dtk_almalinux.def', image_name="dtk_build_almalinux.sif", force=True)

  # Wait until the image is built
  ac_obj=sbwi.run(wait_on_done=True, platform=platform)

  if sbwi.succeeded:
    print("sbi.id: ", sbwi.id)
    # Write ID file
    sbwi.asset_collection.to_id_file(f"{platform._config_block}_dtk_almalinux9_prod.id")
    print("sc: ", ac_obj.id)
    get_files(sbwi.id, "dtk_build_almalinux.sif")


if(__name__ == "__main__"):
  make_work()

