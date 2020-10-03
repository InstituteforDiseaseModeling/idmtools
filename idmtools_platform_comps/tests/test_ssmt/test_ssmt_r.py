import allure
import os
import sys
import pytest
import json

from idmtools_test import COMMON_INPUT_PATH

from idmtools.core.platform_factory import Platform
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools.assets.file_list import FileList
from idmtools_platform_comps.ssmt_work_items.comps_workitems import SSMTWorkItem
from idmtools.core import ItemType
from idmtools.utils.dropbox_location import get_dropbox_location
from idmtools_test.utils.utils import del_folder


@pytest.mark.skip
@pytest.mark.tasks
@pytest.mark.r
@allure.story("COMPS")
@allure.story("SSMT")
class TestRExperiment(ITestWithPersistence):

    def setUp(self) -> None:
        self.platform = Platform('COMPS2')
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        self.input_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "inputs")

    @pytest.mark.skip
    @pytest.mark.comps
    @pytest.mark.long
    def test_r_ssmt_workitem_add_ac_from_path(self):
        # Keep data separate from code in Dropbox
        dropbox_folder = get_dropbox_location()
        data_path = os.path.join(dropbox_folder, "COVID-19", "ncov_public_data")

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

        # verify workitem result
        local_output_path = "output"
        del_folder(local_output_path)
        out_filenames = ["output/stderr.txt"]
        self.platform.get_files_by_id(wi.uid, ItemType.WORKFLOW_ITEM, out_filenames, local_output_path)
        file_path = os.path.join(local_output_path, str(wi.uid))
        self.assertTrue(os.path.exists(os.path.join(file_path, "output", "stderr.txt")))
        self.assertTrue(os.path.exists(os.path.join(file_path, "WorkOrder.json")))
        worker_order = json.load(open(os.path.join(file_path, "WorkOrder.json"), 'r'))
        print(worker_order)
        self.assertEqual(worker_order['WorkItem_Type'], "DockerWorker")
        if not wi.succeeded:
            print(f"Experiment {wi.uid} failed.\n")
            sys.exit(-1)
