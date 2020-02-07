import json
import os
import sys

import pytest
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.ssmt.ssmt_analysis import SSMTAnalysis
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools_test.utils.utils import del_folder

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "inputs"))
from PopulationAnalyzer import PopulationAnalyzer
from AdultVectorsAnalyzer import AdultVectorsAnalyzer


@pytest.mark.comps
class TestSSMTAnalysis(ITestWithPersistence):

    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        print(self.case_name)
        self.platform = Platform('COMPS2')

    def test_ssmt_analysis_PopulationAnalyzer(self):
        experiment_id = "8bb8ae8f-793c-ea11-a2be-f0921c167861"
        analysis = SSMTAnalysis(platform=self.platform,
                                experiment_ids=[experiment_id],
                                analyzers=[PopulationAnalyzer],
                                analyzers_args=[{'name': 'anything'}],
                                analysis_name=self.case_name)

        analysis.analyze(check_status=True)
        wi = analysis.get_work_item()

        # validate output files
        local_output_path = "output"
        del_folder(local_output_path)
        # wi_uid = "cd578e83-2b49-ea11-a2be-f0921c167861"
        out_filenames = ["output/population.png", "output/population.json", "WorkOrder.json"]
        ret = self.platform.get_files_by_id(wi.uid, ItemType.WORKFLOW_ITEM, out_filenames, local_output_path)

        file_path = os.path.join(local_output_path, str(wi.uid))
        self.assertTrue(os.path.exists(os.path.join(file_path, "output", "population.png")))
        self.assertTrue(os.path.exists(os.path.join(file_path, "output", "population.json")))
        self.assertTrue(os.path.exists(os.path.join(file_path, "WorkOrder.json")))
        worker_order = json.load(open(os.path.join(file_path, "WorkOrder.json"), 'r'))
        print(worker_order)
        self.assertEqual(worker_order['WorkItem_Type'], "DockerWorker")
        execution = worker_order['Execution']
        self.assertEqual(execution['Command'],
                         "python analyze_ssmt.py " + experiment_id + " PopulationAnalyzer.PopulationAnalyzer")

    def test_ssmt_analysis_multiple_analyzers(self):
        experiment_id = "8bb8ae8f-793c-ea11-a2be-f0921c167861"
        analysis = SSMTAnalysis(platform=self.platform,
                                experiment_ids=[experiment_id],
                                analyzers=[PopulationAnalyzer, AdultVectorsAnalyzer],
                                analyzers_args=[{'name': 'anything'}, {'name': "adult test"}],
                                analysis_name=self.case_name)

        analysis.analyze(check_status=True)
        wi = analysis.get_work_item()

        # validate output files
        local_output_path = "output"
        del_folder(local_output_path)
        # wi_uid = "cd578e83-2b49-ea11-a2be-f0921c167861"
        out_filenames = ["output/population.png", "output/population.json",
                         "output/adult_vectors.json", "output/adult_vectors.png", "WorkOrder.json"]
        ret = self.platform.get_files_by_id(wi.uid, ItemType.WORKFLOW_ITEM, out_filenames,
                                            local_output_path)

        file_path = os.path.join(local_output_path, str(wi.uid))
        self.assertTrue(os.path.exists(os.path.join(file_path, "output", "population.png")))
        self.assertTrue(os.path.exists(os.path.join(file_path, "output", "population.json")))
        self.assertTrue(os.path.exists(os.path.join(file_path, "output", "adult_vectors.png")))
        self.assertTrue(os.path.exists(os.path.join(file_path, "output", "adult_vectors.json")))

        self.assertTrue(os.path.exists(os.path.join(file_path, "WorkOrder.json")))
        worker_order = json.load(open(os.path.join(file_path, "WorkOrder.json"), 'r'))
        print(worker_order)
        self.assertEqual(worker_order['WorkItem_Type'], "DockerWorker")
        execution = worker_order['Execution']
        self.assertEqual(execution['Command'],
                         "python analyze_ssmt.py " + experiment_id +
                         " PopulationAnalyzer.PopulationAnalyzer,AdultVectorsAnalyzer.AdultVectorsAnalyzer")

    def test_ssmt_analysis_multiple_experiments(self):
        exp_id1 = "8bb8ae8f-793c-ea11-a2be-f0921c167861"
        exp_id2 = "4ea96af7-1549-ea11-a2be-f0921c167861"
        experiment_id = [exp_id1, exp_id2]
        analysis = SSMTAnalysis(platform=self.platform,
                                experiment_ids=experiment_id,
                                analyzers=[PopulationAnalyzer],
                                analyzers_args=[{'name': 'anything'}],
                                analysis_name=self.case_name)

        analysis.analyze(check_status=True)
        wi = analysis.get_work_item()

        # validate output files
        local_output_path = "output"
        del_folder(local_output_path)
        # wi_uid = "cd578e83-2b49-ea11-a2be-f0921c167861"
        out_filenames = ["output/population.png", "output/population.json", "WorkOrder.json"]
        ret = self.platform.get_files_by_id(wi.uid, ItemType.WORKFLOW_ITEM, out_filenames, local_output_path)

        file_path = os.path.join(local_output_path, str(wi.uid))
        self.assertTrue(os.path.exists(os.path.join(file_path, "output", "population.png")))
        self.assertTrue(os.path.exists(os.path.join(file_path, "output", "population.json")))
        self.assertTrue(os.path.exists(os.path.join(file_path, "WorkOrder.json")))
        worker_order = json.load(open(os.path.join(file_path, "WorkOrder.json"), 'r'))
        print(worker_order)
        self.assertEqual(worker_order['WorkItem_Type'], "DockerWorker")
        execution = worker_order['Execution']
        self.assertEqual(execution['Command'],
                         "python analyze_ssmt.py " + exp_id1 + "," + exp_id2 + " PopulationAnalyzer.PopulationAnalyzer")
