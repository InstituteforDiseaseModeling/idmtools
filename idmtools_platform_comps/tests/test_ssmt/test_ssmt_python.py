import json
import os
import sys

import pytest
from idmtools.assets.file_list import FileList
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.managers.work_item_manager import WorkItemManager
from idmtools.ssmt.idm_work_item import SSMTWorkItem
from idmtools.ssmt.ssmt_analysis import SSMTAnalysis
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools_test.utils.utils import del_folder

from examples import EXAMPLES_PATH

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "inputs"))
from SimpleAnalyzer import SimpleAnalyzer
from CSVAnalyzer import CSVAnalyzer



@pytest.mark.comps
class TestSSMTWorkItemPythonExp(ITestWithPersistence):

    def setUp(self):
        print(self._testMethodName)
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        print(self.case_name)
        self.platform = Platform('COMPS2')
        self.tags = {'test': 123}

    def test_ssmt_workitem_python(self):
        command = "python hello.py"
        python_files = os.path.join(EXAMPLES_PATH, "ssmt", "hello_world", "files")
        user_files = FileList(root=python_files)
        wi = SSMTWorkItem(item_name=self.case_name, command=command, user_files=user_files, tags=self.tags)
        wim = WorkItemManager(wi, self.platform)
        wim.process(check_status=True)
        # validate output files
        local_output_path = "output"
        del_folder(local_output_path)
        # wi_uid = "cd578e83-2b49-ea11-a2be-f0921c167861"
        out_filenames = ["hello.py", "WorkOrder.json"]
        ret = self.platform.get_files_by_id(wi.uid, ItemType.WORKFLOW_ITEM, out_filenames, local_output_path)

        file_path = os.path.join(local_output_path, str(wi.uid))
        self.assertTrue(os.path.exists(os.path.join(file_path, "hello.py")))
        self.assertTrue(os.path.exists(os.path.join(file_path, "WorkOrder.json")))
        worker_order = json.load(open(os.path.join(file_path, "WorkOrder.json"), 'r'))
        print(worker_order)
        self.assertEqual(worker_order['WorkItem_Type'], "DockerWorker")
        execution = worker_order['Execution']
        self.assertEqual(execution['Command'],
                         "python hello.py")

    def test_ssmt_workitem_python_simple_analyzer(self):
        experiment_id = "9311af40-1337-ea11-a2be-f0921c167861"
        analysis = SSMTAnalysis(platform=self.platform,
                                experiment_ids=[experiment_id],
                                analyzers=[SimpleAnalyzer],
                                analyzers_args=[{'filenames': ['config.json']}],
                                analysis_name=self.case_name)

        analysis.analyze(check_status=True)
        wi = analysis.get_work_item()
        local_output_path = "output"
        del_folder(local_output_path)
        # wi_uid = "cd578e83-2b49-ea11-a2be-f0921c167861"
        out_filenames = ["output/aggregated_config.json", "WorkOrder.json"]
        ret = self.platform.get_files_by_id(wi.uid, ItemType.WORKFLOW_ITEM, out_filenames, local_output_path)

        file_path = os.path.join(local_output_path, str(wi.uid))
        self.assertTrue(os.path.exists(os.path.join(file_path, "output", "aggregated_config.json")))
        self.assertTrue(os.path.exists(os.path.join(file_path, "WorkOrder.json")))
        worker_order = json.load(open(os.path.join(file_path, "WorkOrder.json"), 'r'))
        print(worker_order)
        self.assertEqual(worker_order['WorkItem_Type'], "DockerWorker")
        execution = worker_order['Execution']
        self.assertEqual(execution['Command'],
                         "python analyze_ssmt.py " + experiment_id + " SimpleAnalyzer.SimpleAnalyzer")

    def test_ssmt_workitem_python_csv_analyzer(self):
        experiment_id = "9311af40-1337-ea11-a2be-f0921c167861"
        analysis = SSMTAnalysis(platform=self.platform,
                                experiment_ids=[experiment_id],
                                analyzers=[CSVAnalyzer],
                                analyzers_args=[{'filenames': ['output/c.csv'],
                                                 'parse': True}],
                                analysis_name=self.case_name)

        analysis.analyze(check_status=True)
        wi = analysis.get_work_item()
        local_output_path = "output"
        del_folder(local_output_path)
        # wi_uid = "cd578e83-2b49-ea11-a2be-f0921c167861"
        out_filenames = ["output/aggregated_c.csv", "WorkOrder.json"]
        ret = self.platform.get_files_by_id(wi.uid, ItemType.WORKFLOW_ITEM, out_filenames, local_output_path)

        file_path = os.path.join(local_output_path, str(wi.uid))
        self.assertTrue(os.path.exists(os.path.join(file_path, "output", "aggregated_c.csv")))
        self.assertTrue(os.path.exists(os.path.join(file_path, "WorkOrder.json")))
        worker_order = json.load(open(os.path.join(file_path, "WorkOrder.json"), 'r'))
        print(worker_order)
        self.assertEqual(worker_order['WorkItem_Type'], "DockerWorker")
        execution = worker_order['Execution']
        self.assertEqual(execution['Command'],
                         "python analyze_ssmt.py " + experiment_id + " CSVAnalyzer.CSVAnalyzer")
