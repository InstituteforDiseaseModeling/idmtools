import json
import os
import pytest
from idmtools.assets.file_list import FileList
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools_platform_comps.ssmt_work_items.comps_workitems import SSMTWorkItem
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools_test.utils.utils import del_folder


@pytest.mark.comps
@pytest.mark.ssmt
class TestSSMTWorkItem(ITestWithPersistence):

    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        print(self.case_name)
        self.platform = Platform('COMPS2')
        self.tags = {'idmtools': self._testMethodName, 'WorkItem type': 'Docker'}
        self.input_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "inputs")

    # test using SSMTWormItem to run PopulationAnalyzer in comps's SSMT DockerWorker
    def test_ssmt_workitem_PopulationAnalyzer(self):
        # load local ("inputs") PopulationAnalyzer.py and run_dtktools_PopulationAnalyzer.py
        # to COMPS's assets
        asset_files = FileList()
        asset_files.add_file(os.path.join(self.input_file_path, 'population_analyzer.py'))
        asset_files.add_file(os.path.join(self.input_file_path, 'run_population_analyzer.py'))

        # load local "input" folder idmtools.ini to current dir in Comps workitem
        user_files = FileList()
        user_files.add_file(os.path.join(self.input_file_path, "idmtools.ini"))

        experiment_id = "8bb8ae8f-793c-ea11-a2be-f0921c167861"
        command = "python Assets/run_population_analyzer.py " + experiment_id
        wi = SSMTWorkItem(item_name=self.case_name, command=command, asset_files=asset_files, user_files=user_files,
                          tags=self.tags)
        self.platform.run_items(wi)
        self.platform.wait_till_done(wi)

        # validate output files
        local_output_path = "output"
        del_folder(local_output_path)
        out_filenames = ["output/population.png", "output/population.json", "WorkOrder.json"]
        self.platform.get_files_by_id(wi.uid, ItemType.WORKFLOW_ITEM, out_filenames, local_output_path)

        file_path = os.path.join(local_output_path, str(wi.uid))
        self.assertTrue(os.path.exists(os.path.join(file_path, "output", "population.png")))
        self.assertTrue(os.path.exists(os.path.join(file_path, "output", "population.json")))
        self.assertTrue(os.path.exists(os.path.join(file_path, "WorkOrder.json")))
        worker_order = json.load(open(os.path.join(file_path, "WorkOrder.json"), 'r'))
        print(worker_order)
        self.assertEqual(worker_order['WorkItem_Type'], "DockerWorker")
        execution = worker_order['Execution']
        self.assertEqual(execution['Command'],
                         "python Assets/run_population_analyzer.py " + experiment_id)

    # test using SSMTWormItem to run multiple analyzers in comps's SSMT DockerWorker
    def test_ssmt_workitem_multiple_analyzers(self):
        # different way to load files to comps than above test case

        # load local ("inputs") files:
        # population_analyzer.py,
        # adult_vectors_analyzer.py,
        # run_dtktools_multiple_analyzers.py
        # to COMPS's workitem current dir
        user_files = FileList()
        user_files.add_file(os.path.join(self.input_file_path, 'population_analyzer.py'))
        user_files.add_file(os.path.join(self.input_file_path, 'adult_vectors_analyzer.py'))
        user_files.add_file(os.path.join(self.input_file_path, 'run_multiple_analyzers.py'))
        user_files.add_file(os.path.join(self.input_file_path, 'idmtools.ini'))

        experiment_id = "8bb8ae8f-793c-ea11-a2be-f0921c167861"
        command = "python run_multiple_analyzers.py " + experiment_id
        wi = SSMTWorkItem(item_name=self.case_name, command=command, user_files=user_files,
                          tags=self.tags)
        self.platform.run_items(wi)
        self.platform.wait_till_done(wi)

        # validate output files
        local_output_path = "output"
        del_folder(local_output_path)
        out_filenames = ["output/population.png", "output/population.json", "WorkOrder.json"]
        self.platform.get_files_by_id(wi.uid, ItemType.WORKFLOW_ITEM, out_filenames, local_output_path)

        # validate output files
        local_output_path = "output_ssmt"
        del_folder(local_output_path)
        out_filenames = ["output/population.png", "output/population.json",
                         "output/adult_vectors.json", "output/adult_vectors.png", "WorkOrder.json"]
        self.platform.get_files_by_id(wi.uid, ItemType.WORKFLOW_ITEM, out_filenames, local_output_path)

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
                         "python run_multiple_analyzers.py " + experiment_id)

    # test using SSMTWormItem to run multiple experiments in comps's SSMT DockerWorker
    def test_ssmt_workitem_multiple_experiments(self):
        exp_id1 = "8bb8ae8f-793c-ea11-a2be-f0921c167861"
        exp_id2 = "4ea96af7-1549-ea11-a2be-f0921c167861"

        # load local ("inputs") population_analyzer.py and run_dtktools_PopulationAnalyzer.py
        # to COMPS's assets
        asset_files = FileList()
        asset_files.add_file(os.path.join(self.input_file_path, 'population_analyzer.py'))
        asset_files.add_file(os.path.join(self.input_file_path, 'run_multiple_exps.py'))

        # load local "input" folder idmtools.ini to current dir in Comps workitem
        user_files = FileList()
        user_files.add_file(os.path.join(self.input_file_path, "idmtools.ini"))

        command = "python Assets/run_multiple_exps.py " + exp_id1 + " " + exp_id2
        wi = SSMTWorkItem(item_name=self.case_name, command=command, asset_files=asset_files, user_files=user_files,
                          tags=self.tags)
        self.platform.run_items(wi)
        self.platform.wait_till_done(wi)

        # validate output files
        local_output_path = "output"
        del_folder(local_output_path)
        out_filenames = ["output/population.png", "output/population.json", "WorkOrder.json"]
        self.platform.get_files_by_id(wi.uid, ItemType.WORKFLOW_ITEM, out_filenames, local_output_path)

        file_path = os.path.join(local_output_path, str(wi.uid))
        self.assertTrue(os.path.exists(os.path.join(file_path, "output", "population.png")))
        self.assertTrue(os.path.exists(os.path.join(file_path, "output", "population.json")))
        self.assertTrue(os.path.exists(os.path.join(file_path, "WorkOrder.json")))
        worker_order = json.load(open(os.path.join(file_path, "WorkOrder.json"), 'r'))
        print(worker_order)
        self.assertEqual(worker_order['WorkItem_Type'], "DockerWorker")
        execution = worker_order['Execution']
        self.assertEqual(execution['Command'],
                         "python Assets/run_multiple_exps.py " + exp_id1 + " " + exp_id2)

    def test_get_files(self):
        wi_id = '63b1822e-1e62-ea11-a2bf-f0921c167862'
        wi = self.platform.get_item(wi_id, ItemType.WORKFLOW_ITEM, raw=False)

        out_filenames = ["output/population.png", "output/population.json", "WorkOrder.json"]
        ret = self.platform.get_files(wi, out_filenames)
        self.assertListEqual(list(ret.keys()), out_filenames)

    def test_get_files_output(self):
        wi_id = '63b1822e-1e62-ea11-a2bf-f0921c167862'
        wi = self.platform.get_item(wi_id, ItemType.WORKFLOW_ITEM, raw=False)

        local_output_path = "output"
        del_folder(local_output_path)
        out_filenames = ["output/population.png", "output/population.json", "WorkOrder.json"]
        self.platform.get_files(wi, out_filenames, local_output_path)

        file_path = os.path.join(local_output_path, str(wi.uid))
        self.assertTrue(os.path.exists(os.path.join(file_path, "output", "population.png")))
        self.assertTrue(os.path.exists(os.path.join(file_path, "output", "population.json")))
        self.assertTrue(os.path.exists(os.path.join(file_path, "WorkOrder.json")))

    def test_get_files_from_id(self):
        wi_id = '63b1822e-1e62-ea11-a2bf-f0921c167862'

        out_filenames = ["output/population.png", "output/population.json", "WorkOrder.json"]
        ret = self.platform.get_files_by_id(wi_id, ItemType.WORKFLOW_ITEM, out_filenames)
        self.assertListEqual(list(ret.keys()), out_filenames)

    def test_get_files_from_id_output(self):
        wi_id = '63b1822e-1e62-ea11-a2bf-f0921c167862'

        local_output_path = "output"
        del_folder(local_output_path)
        out_filenames = ["output/population.png", "output/population.json", "WorkOrder.json"]
        self.platform.get_files_by_id(wi_id, ItemType.WORKFLOW_ITEM, out_filenames, local_output_path)

        file_path = os.path.join(local_output_path, str(wi_id))
        self.assertTrue(os.path.exists(os.path.join(file_path, "output", "population.png")))
        self.assertTrue(os.path.exists(os.path.join(file_path, "output", "population.json")))
        self.assertTrue(os.path.exists(os.path.join(file_path, "WorkOrder.json")))

    def test_get_wi_with_query_criteria_1(self):
        wi_id = '5e2fc03d-2162-ea11-a2bf-f0921c167862'

        cols = ["id", "name", "asset_collection_id"]
        children = ["tags", "files"]

        platform = Platform('COMPS2')
        wi = platform.get_item(wi_id, ItemType.WORKFLOW_ITEM, columns=cols, children=children)
        self.assertIsNotNone(wi.item_name)
        self.assertIsNotNone(wi.asset_collection_id)
        self.assertIsNotNone(wi.tags)
        self.assertIsNotNone(wi.user_files)

    def test_get_wi_with_query_criteria_2(self):
        wi_id = '5e2fc03d-2162-ea11-a2bf-f0921c167862'

        cols = ["id", "name"]
        children = []

        platform = Platform('COMPS2')
        wi = platform.get_item(wi_id, ItemType.WORKFLOW_ITEM, columns=cols, children=children)
        self.assertIsNone(wi.asset_collection_id)
        self.assertIsNone(wi.tags)
        self.assertIsNone(wi.user_files)
