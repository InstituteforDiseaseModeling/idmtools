# This is an example script to generate md5 file from existing sif ac_id in calculon
# For this example, we will save file name as dtk_run_rocky_py39.sif.md5 which contains md5 of dtk_run_rocky_py39.sif
# Later, we can use this md5 file in emodpy related script like this: task.set_sif(dtk_run_rocky_py39.sif.md5) to
# set the singularity sif file for the task

from idmtools.core.platform_factory import Platform
from idmtools_platform_comps.utils.general import save_sif_asset_md5_from_ac_id

platform = Platform("Calculon")
# Save md5 file with existing ac_id
# fabcee1d-045a-ed11-a9ff-b88303911bc1 is ac id for dtk_run_rocky_py39.sif in calculon
save_sif_asset_md5_from_ac_id("fabcee1d-045a-ed11-a9ff-b88303911bc1")
