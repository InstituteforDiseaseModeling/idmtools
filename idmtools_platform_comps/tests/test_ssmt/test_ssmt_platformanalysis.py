import allure
import json
import os
import sys

import pytest
from idmtools.analysis.platform_anaylsis import PlatformAnalysis
from idmtools.core.platform_factory import Platform
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools.core import ItemType

analyzer_path = os.path.join(os.path.dirname(__file__), "..", "inputs")
sys.path.insert(0, analyzer_path)
from simple_analyzer import SimpleAnalyzer  # noqa
from csv_analyzer import CSVAnalyzer  # noqa
from infectiousness_csv_analyzer import InfectiousnessCSVAnalyzer  # noqa
from node_csv_analyzer import NodeCSVAnalyzer  # noqa


@pytest.mark.comps
@pytest.mark.ssmt
@allure.story("COMPS")
@allure.story("Analyzers")
@allure.story("PlatformAnalysis")
@allure.story("SSMT")
@allure.suite("idmtools_platform_comps")
class TestPlatformAnalysis(ITestWithPersistence):

    def setUp(self):
        print(self._testMethodName)
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        print(self.case_name)
        self.platform = Platform('COMPS2')
        self.tags = {'idmtools': self._testMethodName, 'WorkItem type': 'Docker'}
        self.input_file_path = analyzer_path

    # Test SimpleAnalyzer with SSMTAnalysis which analyzes python experiment's results
    @pytest.mark.smoke
    def test_ssmt_workitem_python_simple_analyzer(self):
        experiment_id = '9311af40-1337-ea11-a2be-f0921c167861'  # comps2 exp id
        # experiment_id = 'de07f612-69ed-ea11-941f-0050569e0ef3'  # idmtvapp17
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
        out_filenames = ["output/aggregated_config.json", "WorkOrder.json"]
        self.platform.get_files_by_id(wi.uid, ItemType.WORKFLOW_ITEM, out_filenames, local_output_path)

        file_path = os.path.join(local_output_path, wi.id)
        self.assertTrue(os.path.exists(os.path.join(file_path, "output", "aggregated_config.json")))
        self.assertTrue(os.path.exists(os.path.join(file_path, "WorkOrder.json")))
        worker_order = json.load(open(os.path.join(file_path, "WorkOrder.json"), 'r'))
        self.assertEqual(worker_order['WorkItem_Type'], "DockerWorker")
        execution = worker_order['Execution']
        self.assertEqual(execution['Command'],
                         "python platform_analysis_bootstrap.py " + experiment_id + " simple_analyzer.SimpleAnalyzer comps2")

    # Test CSVAnalyzer with SSMTAnalysis which analyzes python experiment's results
    def test_ssmt_workitem_python_csv_analyzer(self):
        experiment_id = '9311af40-1337-ea11-a2be-f0921c167861'  # comps2 exp id
        # experiment_id = 'de07f612-69ed-ea11-941f-0050569e0ef3'  # idmtvapp17
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
        out_filenames = ["output/aggregated_c.csv", "WorkOrder.json"]
        self.platform.get_files_by_id(wi.uid, ItemType.WORKFLOW_ITEM, out_filenames, local_output_path)

        file_path = os.path.join(local_output_path, wi.id)
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
        exp_id = "a980f265-995e-ea11-a2bf-f0921c167862"  # comps2 exp id
        # exp_id = "b2a31828-78ed-ea11-941f-0050569e0ef3"  # idmtvapp17
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
        out_filenames = [exp_id + "/InfectiousnessCSVAnalyzer.csv", exp_id + "/NodeCSVAnalyzer.csv", "WorkOrder.json"]
        self.platform.get_files_by_id(wi.uid, ItemType.WORKFLOW_ITEM, out_filenames, local_output_path)

        file_path = os.path.join(local_output_path, str(wi.uid))
        self.assertTrue(os.path.exists(os.path.join(file_path, exp_id, "InfectiousnessCSVAnalyzer.csv")))
        self.assertTrue(os.path.exists(os.path.join(file_path, exp_id, "NodeCSVAnalyzer.csv")))
        worker_order = json.load(open(os.path.join(file_path, "WorkOrder.json"), 'r'))
        print(worker_order)
        self.assertEqual(worker_order['WorkItem_Type'], "DockerWorker")
        execution = worker_order['Execution']
        self.assertEqual(execution['Command'],
                         "python platform_analysis_bootstrap.py " + exp_id + " infectiousness_csv_analyzer.InfectiousnessCSVAnalyzer,node_csv_analyzer.NodeCSVAnalyzer comps2")

    @pytest.mark.comps
    def test_ssmt_seir_model_analysis_single_script(self):
        exp_id = "a980f265-995e-ea11-a2bf-f0921c167862"  # comps2 exp id
        # exp_id = "b2a31828-78ed-ea11-941f-0050569e0ef3"  # idmtvapp17
        filenames = {'filenames': ['output/individual.csv']}
        filenames_2 = {'filenames': ['output/node.csv']}

        # Initialize two analyser classes with the path of the output csv file
        from custom_csv_analyzer import InfectiousnessCSVAnalyzer, NodeCSVAnalyzer
        analyzers = [InfectiousnessCSVAnalyzer, NodeCSVAnalyzer]
        analysis = PlatformAnalysis(platform=self.platform,
                                    experiment_ids=[exp_id],
                                    analyzers=analyzers,
                                    analyzers_args=[filenames, filenames_2],
                                    analysis_name=self.case_name,
                                    tags={'idmtools': self._testMethodName, 'WorkItem type': 'Docker'})

        analysis.analyze(check_status=True)
        wi = analysis.get_work_item()

        # Verify workitem results
        local_output_path = "output"
        out_filenames = [exp_id + "/InfectiousnessCSVAnalyzer.csv", exp_id + "/NodeCSVAnalyzer.csv", "WorkOrder.json"]
        self.platform.get_files_by_id(wi.uid, ItemType.WORKFLOW_ITEM, out_filenames, local_output_path)

        file_path = os.path.join(local_output_path, str(wi.uid))
        self.assertTrue(os.path.exists(os.path.join(file_path, exp_id, "InfectiousnessCSVAnalyzer.csv")))
        self.assertTrue(os.path.exists(os.path.join(file_path, exp_id, "NodeCSVAnalyzer.csv")))
        worker_order = json.load(open(os.path.join(file_path, "WorkOrder.json"), 'r'))
        print(worker_order)
        self.assertEqual(worker_order['WorkItem_Type'], "DockerWorker")
        execution = worker_order['Execution']
        self.assertEqual(execution['Command'],
                         "python platform_analysis_bootstrap.py " + exp_id + " custom_csv_analyzer.InfectiousnessCSVAnalyzer,custom_csv_analyzer.NodeCSVAnalyzer comps2")
