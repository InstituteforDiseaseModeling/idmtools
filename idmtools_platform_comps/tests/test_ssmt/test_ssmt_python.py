import json
import os
import sys

import pytest
from idmtools.assets.file_list import FileList
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.managers.work_item_manager import WorkItemManager
from idmtools_platform_comps.ssmt_work_items.comps_workitems import SSMTWorkItem
from idmtools.analysis.platform_anaylsis import PlatformAnalysis
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools_test.utils.utils import del_folder


# import analyzers from current dir's inputs dir
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), "inputs"))
# from SimpleAnalyzer import SimpleAnalyzer
# from CSVAnalyzer import CSVAnalyzer


@pytest.mark.comps
class TestSSMTWorkItemPythonExp(ITestWithPersistence):

    def setUp(self):
        print(self._testMethodName)
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        print(self.case_name)
        self.platform = Platform('COMPS2')
        self.tags = {'idmtools': self._testMethodName, 'WorkItem type': 'Docker'}
        self.input_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inputs")

    # test SSMTWorkItem with simple python script "hello.py"
    # "hello.py" will run in comps's workitem worker like running it in local:
    # python hello.py
    def test_ssmt_workitem_python(self):
        command = "python hello.py"
        user_files = FileList()
        user_files.add_file(os.path.join(self.input_file_path, "hello.py"))

        wi = SSMTWorkItem(item_name=self.case_name, command=command, user_files=user_files, tags=self.tags)
        wim = WorkItemManager(wi, self.platform)
        wim.process(check_status=True)

        # verify workitem output files
        local_output_path = "output"  # local output dir
        del_folder(local_output_path)  # delete existing folder before run validation
        out_filenames = ["hello.py", "WorkOrder.json"]  # files to retrieve from workitem dir
        ret = self.platform.get_files_by_id(wi.uid, ItemType.WORKFLOW_ITEM, out_filenames, local_output_path)

        file_path = os.path.join(local_output_path, str(wi.uid))
        # verify that we do retrieved the correct files from comps' workitem to local
        self.assertTrue(os.path.exists(os.path.join(file_path, "hello.py")))
        self.assertTrue(os.path.exists(os.path.join(file_path, "WorkOrder.json")))

        # verify that WorkOrder.json content is correct
        worker_order = json.load(open(os.path.join(file_path, "WorkOrder.json"), 'r'))
        print(worker_order)
        self.assertEqual(worker_order['WorkItem_Type'], "DockerWorker")
        execution = worker_order['Execution']
        self.assertEqual(execution['Command'],
                         "python hello.py")

    # Test SimpleAnalyzer with SSMTAnalysis which analyzes python experiment's results
    def test_ssmt_workitem_python_simple_analyzer(self):
        sys.path.insert(0, self.input_file_path)
        from SimpleAnalyzer import SimpleAnalyzer

        experiment_id = "9311af40-1337-ea11-a2be-f0921c167861"
        analysis = PlatformAnalysis(platform=self.platform,
                                    experiment_ids=[experiment_id],
                                    analyzers=[SimpleAnalyzer],
                                    analyzers_args=[{'filenames': ['config.json']}],
                                    analysis_name=self.case_name,
                                    tags={'idmtools': self._testMethodName, 'WorkItem type': 'Docker'})

        analysis.analyze(check_status=True)
        wi = analysis.get_work_item()

        # verify workitem result
        local_output_path = "output"
        del_folder(local_output_path)
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
                         "python platform_analysis_bootstrap.py " + experiment_id + " SimpleAnalyzer.SimpleAnalyzer")

    # Test CSVAnalyzer with SSMTAnalysis which analyzes python experiment's results
    def test_ssmt_workitem_python_csv_analyzer(self):
        sys.path.insert(0, self.input_file_path)
        from CSVAnalyzer import CSVAnalyzer
        experiment_id = "9311af40-1337-ea11-a2be-f0921c167861"
        analysis = PlatformAnalysis(platform=self.platform,
                                    experiment_ids=[experiment_id],
                                    analyzers=[CSVAnalyzer],
                                    analyzers_args=[{'filenames': ['output/c.csv'],
                                                 'parse': True}],
                                    analysis_name=self.case_name,
                                    tags={'idmtools': self._testMethodName, 'WorkItem type': 'Docker'})

        analysis.analyze(check_status=True)
        wi = analysis.get_work_item()

        # verify workitem result
        local_output_path = "output"
        del_folder(local_output_path)
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
                         "python platform_analysis_bootstrap.py " + experiment_id + " CSVAnalyzer.CSVAnalyzer")
