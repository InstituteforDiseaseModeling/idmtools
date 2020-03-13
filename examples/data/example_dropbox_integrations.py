import os
from idmtools_test import COMMON_INPUT_PATH

from idmtools.core.platform_factory import Platform
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools.assets.file_list import FileList
from idmtools_platform_comps.ssmt_work_items.comps_workitems import SSMTWorkItem

from idmtools_core.idmtools.utils.dropbox_location import get_dropbox_location


class ExampleDropboxIntegrations(ITestWithPersistence):

    def setUp(self) -> None:
        self.platform = Platform('COMPS2')
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        self.input_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "inputs")

    def example_r_ssmt_workitem_add_ac_from_path(self):
        # Keep data separate from code in Dropbox
        dropbox_folder = get_dropbox_location()
        data_path = os.path.join(dropbox_folder, "COVID-19", "data", "ncov_public_data")

        # R script path
        ac_lib_path = os.path.join(COMMON_INPUT_PATH, "r", "ncov_analysis")

        # load assets to COMPS's assets
        asset_files = FileList()
        asset_files.add_path(ac_lib_path, relative_path="ncov_analysis", recursive=True)
        asset_files.add_file(
            os.path.join(data_path, "Kudos to DXY.cn Last update_ 01_25_2020,  11_30 am (EST) - Line-list.csv"))

        # load local "input" folder simtools.ini to current dir in Comps workitem
        user_files = FileList()
        user_files.add_file(os.path.join(self.input_file_path, "idmtools.ini"))

        self.tags = {'idmtools': self._testMethodName, 'WorkItem type': 'Docker'}
        # RScript to run from /usr/bin on COMPS SSMT Docker server
        command = "/usr/bin/Rscript Assets/ncov_analysis/individual_dynamics_estimates/estimate_incubation_period.R"
        wi = SSMTWorkItem(item_name=self.case_name, command=command, asset_files=asset_files, user_files=user_files,
                          tags=self.tags, docker_image="ubuntu18.04_r3.5.0")
        wi.run(True, platform=self.platform)
