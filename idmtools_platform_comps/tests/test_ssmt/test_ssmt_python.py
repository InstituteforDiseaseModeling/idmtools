import json
import os
import sys

import pytest
from idmtools.analysis.platform_anaylsis import PlatformAnalysis
from idmtools.assets.file_list import FileList
from idmtools.core.platform_factory import Platform
from idmtools_platform_comps.ssmt_work_items.comps_workitems import SSMTWorkItem
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools_test.utils.utils import del_folder
from idmtools.core import ItemType

# import analyzers from current dir's inputs dir
analyzer_path = os.path.join(os.path.dirname(__file__), "..", "inputs")
sys.path.insert(0, analyzer_path)
from simple_analyzer import SimpleAnalyzer  # noqa
from csv_analyzer import CSVAnalyzer  # noqa
from infectiousness_csv_analyzer import InfectiousnessCSVAnalyzer  # noqa
from node_csv_analyzer import NodeCSVAnalyzer  # noqa


@pytest.mark.comps
@pytest.mark.ssmt
class TestSSMTWorkItemPythonExp(ITestWithPersistence):

    def setUp(self):
        print(self._testMethodName)
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        print(self.case_name)
        self.platform = Platform('COMPS2')
        self.tags = {'idmtools': self._testMethodName, 'WorkItem type': 'Docker'}
        self.input_file_path = analyzer_path

    # test SSMTWorkItem with simple python script "hello.py"
    # "hello.py" will run in comps's workitem worker like running it in local:
    # python hello.py
    def test_ssmt_workitem_python(self):
        command = "python hello.py"
        user_files = FileList()
        user_files.add_file(os.path.join(self.input_file_path, "hello.py"))

        wi = SSMTWorkItem(item_name=self.case_name, command=command, user_files=user_files, tags=self.tags)
        self.platform.run_items(wi)
        self.platform.wait_till_done(wi)

        # verify workitem output files
        local_output_path = "output"  # local output dir
        del_folder(local_output_path)  # delete existing folder before run validation
        out_filenames = ["hello.py", "WorkOrder.json"]  # files to retrieve from workitem dir
        self.platform.get_files_by_id(wi.uid, ItemType.WORKFLOW_ITEM, out_filenames, local_output_path)

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
        self.platform.get_files_by_id(wi.uid, ItemType.WORKFLOW_ITEM, out_filenames, local_output_path)

        file_path = os.path.join(local_output_path, str(wi.uid))
        self.assertTrue(os.path.exists(os.path.join(file_path, "output", "aggregated_config.json")))
        self.assertTrue(os.path.exists(os.path.join(file_path, "WorkOrder.json")))
        worker_order = json.load(open(os.path.join(file_path, "WorkOrder.json"), 'r'))
        print(worker_order)
        self.assertEqual(worker_order['WorkItem_Type'], "DockerWorker")
        execution = worker_order['Execution']
        self.assertEqual(execution['Command'],
                         "python platform_analysis_bootstrap.py " + experiment_id +
                         " simple_analyzer.SimpleAnalyzer comps2")

    # Test CSVAnalyzer with SSMTAnalysis which analyzes python experiment's results
    def test_ssmt_workitem_python_csv_analyzer(self):
        experiment_id = "9311af40-1337-ea11-a2be-f0921c167861"
        analysis = PlatformAnalysis(platform=self.platform,
                                    experiment_ids=[experiment_id],
                                    analyzers=[CSVAnalyzer],
                                    analyzers_args=[{'filenames': ['output/c.csv'], 'parse': True}],
                                    analysis_name=self.case_name,
                                    tags={'idmtools': self._testMethodName, 'WorkItem type': 'Docker'})

        analysis.analyze(check_status=True)
        wi = analysis.get_work_item()

        # verify workitem result
        local_output_path = "output"
        del_folder(local_output_path)
        out_filenames = ["output/aggregated_c.csv", "WorkOrder.json"]
        self.platform.get_files_by_id(wi.uid, ItemType.WORKFLOW_ITEM, out_filenames, local_output_path)

        file_path = os.path.join(local_output_path, str(wi.uid))
        self.assertTrue(os.path.exists(os.path.join(file_path, "output", "aggregated_c.csv")))
        self.assertTrue(os.path.exists(os.path.join(file_path, "WorkOrder.json")))
        worker_order = json.load(open(os.path.join(file_path, "WorkOrder.json"), 'r'))
        print(worker_order)
        self.assertEqual(worker_order['WorkItem_Type'], "DockerWorker")
        execution = worker_order['Execution']
        self.assertEqual(execution['Command'],
                         "python platform_analysis_bootstrap.py " + experiment_id + " csv_analyzer.CSVAnalyzer comps2")

    @pytest.mark.comps
    def test_ssmt_seir_model_analysis(self):
        exp_id = 'a980f265-995e-ea11-a2bf-f0921c167862'  # comps2 staging exp id
        filenames = {'filenames': ['output/individual.csv']}
        filenames_2 = {'filenames': ['output/node.csv']}
        analysis = PlatformAnalysis(platform=self.platform,
                                    experiment_ids=[exp_id],
                                    analyzers=[InfectiousnessCSVAnalyzer, NodeCSVAnalyzer],
                                    analyzers_args=[filenames, filenames_2],
                                    analysis_name=self.case_name,
                                    tags={'idmtools': self._testMethodName, 'WorkItem type': 'Docker'})

        analysis.analyze(check_status=True)
        wi = analysis.get_work_item()

        # Verify workitem results
        local_output_path = "output"
        del_folder(local_output_path)
        out_filenames = [exp_id + "/InfectiousnessCSVAnalyzer.csv", exp_id + "/NodeCSVAnalyzer.csv", "WorkOrder.json"]
        ret = self.platform.get_files_by_id(wi.uid, ItemType.WORKFLOW_ITEM, out_filenames, local_output_path)

        file_path = os.path.join(local_output_path, str(wi.uid))
        self.assertTrue(os.path.exists(os.path.join(file_path, exp_id, "InfectiousnessCSVAnalyzer.csv")))
        self.assertTrue(os.path.exists(os.path.join(file_path, exp_id, "NodeCSVAnalyzer.csv")))
        worker_order = json.load(open(os.path.join(file_path, "WorkOrder.json"), 'r'))
        print(worker_order)
        self.assertEqual(worker_order['WorkItem_Type'], "DockerWorker")
        execution = worker_order['Execution']
        self.assertEqual(execution['Command'],
                         "python platform_analysis_bootstrap.py " + exp_id +
                         " infectiousness_csv_analyzer.InfectiousnessCSVAnalyzer,node_csv_analyzer.NodeCSVAnalyzer comps2")

    @pytest.mark.skip
    @pytest.mark.comps
    # TODO: Issue 663 SSMT PlatformAnalysis cannot put 2 analyzers in same file as main entry
    def test_ssmt_seir_model_analysis_single_script(self):
        exp_id = 'a980f265-995e-ea11-a2bf-f0921c167862'  # comps2 staging exp id
        # filenames = {'filenames': ['output/individual.csv']}
        # filenames_2 = {'filenames': ['output/node.csv']}
        filenames = ['output/individual.csv']
        filenames_2 = ['output/node.csv']
        # Initialize two analyser classes with the path of the output csv file
        from custom_csv_analyzer import InfectiousnessCSVAnalyzer, NodeCSVAnalyzer
        analyzers = [InfectiousnessCSVAnalyzer(filenames=filenames), NodeCSVAnalyzer(filenames=filenames_2)]
        analysis = PlatformAnalysis(platform=self.platform,
                                    experiment_ids=[exp_id],
                                    analyzers=analyzers,
                                    # analyzers=[InfectiousnessCSVAnalyzer, NodeCSVAnalyzer],
                                    analyzers_args=[filenames, filenames_2],
                                    analysis_name=self.case_name,
                                    tags={'idmtools': self._testMethodName, 'WorkItem type': 'Docker'})

        analysis.analyze(check_status=True)
        wi = analysis.get_work_item()

        # Verify workitem results
        local_output_path = "output"
        del_folder(local_output_path)
        out_filenames = [exp_id + "/InfectiousnessCSVAnalyzer.csv", exp_id + "/NodeCSVAnalyzer.csv", "WorkOrder.json"]
        ret = self.platform.get_files_by_id(wi.uid, ItemType.WORKFLOW_ITEM, out_filenames, local_output_path)

        file_path = os.path.join(local_output_path, str(wi.uid))
        self.assertTrue(os.path.exists(os.path.join(file_path, exp_id, "InfectiousnessCSVAnalyzer.csv")))
        self.assertTrue(os.path.exists(os.path.join(file_path, exp_id, "NodeCSVAnalyzer.csv")))
        worker_order = json.load(open(os.path.join(file_path, "WorkOrder.json"), 'r'))
        print(worker_order)
        self.assertEqual(worker_order['WorkItem_Type'], "DockerWorker")
        execution = worker_order['Execution']
        self.assertEqual(execution['Command'],
                         "python platform_analysis_bootstrap.py " + exp_id +
                         " custom_csv_analyzer.InfectiousnessCSVAnalyzer,custom_csv_analyzer.NodeCSVAnalyzer comps2")
