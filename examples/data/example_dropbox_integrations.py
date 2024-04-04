# Example Dropbox Integration
# In this example, we will demonstrate how to use your local Dropbox location for your model or analysis' data files
# This example uses an SSMT Work Item, but you can do the same for your Experiments/Simulations

# First, import some necessary system and idmtools packages.
import os
from idmtools.assets import AssetCollection
from idmtools_test import COMMON_INPUT_PATH
from idmtools.core.platform_factory import Platform

from idmtools_platform_comps.ssmt_work_items.comps_workitems import SSMTWorkItem
from idmtools_core.idmtools.utils.dropbox_location import get_dropbox_location


if __name__ == '__main__':

    # In order to run the SSMT work item, we need to set a `Platform`
    platform = Platform('CALCULON')
    case_name = os.path.basename(__file__) + "--" + 'example_r_ssmt_workitem_add_ac_from_dropbox_path'
    input_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

    # Keep data separate from code in Dropbox
    dropbox_folder = get_dropbox_location()
    data_path = os.path.join(dropbox_folder, "COVID-19", "data", "ncov_public_data")

    # R script path
    ac_lib_path = os.path.join(COMMON_INPUT_PATH, "r", "ncov_analysis")

    # load assets to COMPS's assets
    asset_files = AssetCollection()
    asset_files.add_directory(ac_lib_path, relative_path="ncov_analysis", recursive=True)
    asset_files.add_asset(os.path.join(data_path, "Kudos to DXY.cn Last update_ 01_25_2020,  11_30 am (EST) - Line-list.csv"))

    # load local "input" folder simtools.ini to current dir in Comps workitem
    user_files = AssetCollection()
    user_files.add_asset(os.path.join(input_file_path, "idmtools.ini"))

    tags = {'idmtools': case_name, 'WorkItem type': 'Docker'}
    # RScript to run from /usr/bin on COMPS SSMT Docker server
    command = "/usr/bin/Rscript Assets/ncov_analysis/individual_dynamics_estimates/estimate_incubation_period.R"
    wi = SSMTWorkItem(name=case_name, command=command, assets=asset_files, transient_assets=user_files, tags=tags, docker_image="ubuntu18.04_r3.5.0")
    wi.run(True, platform=platform)
