import json
import os

import pytest
from idmtools.analysis.download_analyzer import DownloadAnalyzer
from idmtools.assets.file_list import FileList
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools_platform_comps.ssmt_work_items.comps_workitems import SSMTWorkItem
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools.analysis.analyze_manager import AnalyzeManager


@pytest.mark.comps
@pytest.mark.ssmt
class TestSSMTWorkItem(ITestWithPersistence):

    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        print(self.case_name)
        self.platform = Platform('COMPS2')
        self.tags = {'idmtools': self._testMethodName, 'WorkItem type': 'Docker'}
        self.input_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "inputs")

    # test SSMTWorkItem with simple python script "hello.py"
    # "hello.py" will run in comps's workitem worker like running it in local:
    # python hello.py
    def test_ssmt_workitem_python(self):
        command = "python hello.py"
        user_files = FileList()
        user_files.add_file(os.path.join(self.input_file_path, "hello.py"))

        wi = SSMTWorkItem(item_name=self.case_name, command=command, user_files=user_files, tags=self.tags)
        wi.run(wait_on_done=True)

        # verify workitem output files
        local_output_path = "output"  # local output dir
        out_filenames = ["hello.py", "WorkOrder.json"]  # files to retrieve from workitem dir
        self.platform.get_files_by_id(wi.uid, ItemType.WORKFLOW_ITEM, out_filenames, local_output_path)

        # verify that we do retrieved the correct files from comps' workitem to local
        self.assertTrue(os.path.exists(os.path.join("output", wi.id, "hello.py")))
        self.assertTrue(os.path.exists(os.path.join("output", wi.id, "WorkOrder.json")))

        # verify that WorkOrder.json content is correct
        worker_order = json.load(open(os.path.join("output", wi.id, "WorkOrder.json"), 'r'))
        print(worker_order)
        self.assertEqual(worker_order['WorkItem_Type'], "DockerWorker")
        execution = worker_order['Execution']
        self.assertEqual(execution['Command'],
                         "python hello.py")

    # test using SSMTWormItem to run PopulationAnalyzer in comps's SSMT DockerWorker
    @pytest.mark.smoke
    def test_ssmt_workitem_PopulationAnalyzer(self):
        # load local ("inputs") PopulationAnalyzer.py and run_dtktools_PopulationAnalyzer.py
        # to COMPS's assets
        asset_files = FileList()
        asset_files.add_file(os.path.join(self.input_file_path, 'population_analyzer.py'))
        asset_files.add_file(os.path.join(self.input_file_path, 'run_population_analyzer.py'))

        # load local "input" folder idmtools.ini to current dir in Comps workitem
        user_files = FileList()
        user_files.add_file(os.path.join(self.input_file_path, "idmtools.ini"))

        experiment_id = "8bb8ae8f-793c-ea11-a2be-f0921c167861"  # COMPS2 exp
        # experiment_id = "18553481-1f42-ea11-941b-0050569e0ef3"  # idmtvapp17 exp
        command = "python Assets/run_population_analyzer.py " + experiment_id
        wi = SSMTWorkItem(item_name=self.case_name, command=command, asset_files=asset_files, user_files=user_files,
                          tags=self.tags)
        wi.run(wait_on_done=True)

        # validate output files
        local_output_path = "output"
        out_filenames = ["output/" + experiment_id + "/population.png", "output/" + experiment_id + "/population.json",
                         "WorkOrder.json"]
        self.platform.get_files_by_id(wi.uid, ItemType.WORKFLOW_ITEM, out_filenames, local_output_path)

        file_path = os.path.join(local_output_path, wi.id)
        self.assertTrue(os.path.exists(os.path.join(file_path, "output", experiment_id, "population.png")))
        self.assertTrue(os.path.exists(os.path.join(file_path, "output", experiment_id, "population.json")))
        self.assertTrue(os.path.exists(os.path.join(file_path, "WorkOrder.json")))
        with open(os.path.join(file_path, "WorkOrder.json"), 'r') as f:
            worker_order = json.load(f)
            print(worker_order)
            self.assertEqual(worker_order['WorkItem_Type'], "DockerWorker")
            execution = worker_order['Execution']
            self.assertEqual(execution['Command'], "python Assets/run_population_analyzer.py " + experiment_id)

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

        experiment_id = "8bb8ae8f-793c-ea11-a2be-f0921c167861"  # COMPS2 exp
        # experiment_id = "18553481-1f42-ea11-941b-0050569e0ef3"  # idmtvapp17 exp
        command = "python run_multiple_analyzers.py " + experiment_id
        wi = SSMTWorkItem(item_name=self.case_name, command=command, user_files=user_files,
                          tags=self.tags)
        wi.run(wait_on_done=True)

        # validate output files
        local_output_path = "output"
        out_filenames = ["output/" + experiment_id + "/population.png", "output/" + experiment_id + "/population.json",
                         "output/" + experiment_id + "/adult_vectors.json",
                         "output/" + experiment_id + "/adult_vectors.png", "WorkOrder.json"]
        self.platform.get_files_by_id(wi.uid, ItemType.WORKFLOW_ITEM, out_filenames, local_output_path)

        file_path = os.path.join(local_output_path, wi.id)
        self.assertTrue(os.path.exists(os.path.join(file_path, "output", experiment_id,  "population.png")))
        self.assertTrue(os.path.exists(os.path.join(file_path, "output", experiment_id, "population.json")))
        self.assertTrue(os.path.exists(os.path.join(file_path, "output", experiment_id, "adult_vectors.png")))
        self.assertTrue(os.path.exists(os.path.join(file_path, "output", experiment_id, "adult_vectors.json")))

        self.assertTrue(os.path.exists(os.path.join(file_path, "WorkOrder.json")))
        with open(os.path.join(file_path, "WorkOrder.json"), 'r') as f:
            worker_order = json.load(f)
            print(worker_order)
            self.assertEqual(worker_order['WorkItem_Type'], "DockerWorker")
            execution = worker_order['Execution']
            self.assertEqual(execution['Command'], "python run_multiple_analyzers.py " + experiment_id)

    # test using SSMTWormItem to run multiple experiments in comps's SSMT DockerWorker
    @pytest.mark.skip("need emodpy")
    def test_ssmt_workitem_multiple_experiments(self):
        exp_id1 = "4ea96af7-1549-ea11-a2be-f0921c167861"  # comps2 exp
        exp_id2 = "8bb8ae8f-793c-ea11-a2be-f0921c167861"  # comps2 exp

        # exp_id1 = "18553481-1f42-ea11-941b-0050569e0ef3"  # idmtvapp17 exp
        # exp_id2 = "a741698b-74ed-ea11-941f-0050569e0ef3"  # idmtvapp17 exp
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
        wi.run(wait_on_done=True)

        # validate output files
        local_output_path = "output"
        out_filenames = ["output/" + exp_id1 + "/population.png", "output/" + exp_id1 + "/population.json",
                         "WorkOrder.json"]
        self.platform.get_files_by_id(wi.uid, ItemType.WORKFLOW_ITEM, out_filenames, local_output_path)

        file_path = os.path.join(local_output_path, wi.id)
        self.assertTrue(os.path.exists(os.path.join(file_path, "output", exp_id1, "population.png")))
        self.assertTrue(os.path.exists(os.path.join(file_path, "output", exp_id1, "population.json")))
        self.assertTrue(os.path.exists(os.path.join(file_path, "WorkOrder.json")))
        with open(os.path.join(file_path, "WorkOrder.json"), 'r') as f:
            worker_order = json.load(f)
            print(worker_order)
            self.assertEqual(worker_order['WorkItem_Type'], "DockerWorker")
            execution = worker_order['Execution']
            self.assertEqual(execution['Command'], "python Assets/run_multiple_exps.py " + exp_id1 + " " + exp_id2)

    @pytest.mark.comps
    def test_ssmt_seir_model_analysis_single_script(self):
        exp_id = "a980f265-995e-ea11-a2bf-f0921c167862"  # comps2 staging exp id
        # exp_id = "b2a31828-78ed-ea11-941f-0050569e0ef3"  # idmtvapp17
        user_files = FileList()
        user_files.add_file(os.path.join(self.input_file_path, 'custom_csv_analyzer.py'))
        user_files.add_file(os.path.join(self.input_file_path, 'run_multiple_analyzers_single_script.py'))
        user_files.add_file(os.path.join(self.input_file_path, 'idmtools.ini'))

        command = "python run_multiple_analyzers_single_script.py " + exp_id
        wi = SSMTWorkItem(item_name=self.case_name, command=command, user_files=user_files,
                          tags=self.tags)
        wi.run(True, platform=self.platform)

        # Verify workitem results
        local_output_path = "output"
        out_filenames = [exp_id + "/InfectiousnessCSVAnalyzer.csv",
                         exp_id + "/NodeCSVAnalyzer.csv",
                         exp_id + "/InfectiousnessCSVAnalyzer.png",
                         exp_id + "/NodeCSVAnalyzer.png", "WorkOrder.json"]
        self.platform.get_files_by_id(wi.uid, ItemType.WORKFLOW_ITEM, out_filenames, local_output_path)

        file_path = os.path.join(local_output_path, wi.id)
        self.assertTrue(os.path.exists(os.path.join(file_path, exp_id, "InfectiousnessCSVAnalyzer.csv")))
        self.assertTrue(os.path.exists(os.path.join(file_path, exp_id, "NodeCSVAnalyzer.csv")))
        self.assertTrue(os.path.exists(os.path.join(file_path, exp_id, "InfectiousnessCSVAnalyzer.png")))
        self.assertTrue(os.path.exists(os.path.join(file_path, exp_id, "NodeCSVAnalyzer.png")))
        with open(os.path.join(file_path, "WorkOrder.json"), 'r') as f:
            worker_order = json.load(f)
            print(worker_order)
            self.assertEqual(worker_order['WorkItem_Type'], "DockerWorker")
            execution = worker_order['Execution']
            self.assertEqual(execution['Command'], "python run_multiple_analyzers_single_script.py "+ exp_id)

    def test_get_files(self):
        wi_id = '5e2fc03d-2162-ea11-a2bf-f0921c167862'  # comps2 wi_id
        # wi_id = '5f7a43d8-6aed-ea11-941f-0050569e0ef3'  # idmtvapp17 wi_id
        wi = self.platform.get_item(wi_id, ItemType.WORKFLOW_ITEM, raw=False)

        out_filenames = ["output/population.png", "output/population.json", "WorkOrder.json"]
        ret = self.platform.get_files(wi, out_filenames)
        self.assertListEqual(list(ret.keys()), out_filenames)

    def test_get_files_output(self):
        wi_id = '63b1822e-1e62-ea11-a2bf-f0921c167862'  # comps2 wi_id
        # wi_id = '5f7a43d8-6aed-ea11-941f-0050569e0ef3'  # idmtvapp17 wi_id
        wi = self.platform.get_item(wi_id, ItemType.WORKFLOW_ITEM, raw=False)

        local_output_path = "output"
        out_filenames = ["output/population.png", "output/population.json", "WorkOrder.json"]
        self.platform.get_files(wi, out_filenames, local_output_path)

        file_path = os.path.join(local_output_path, str(wi.uid))
        self.assertTrue(os.path.exists(os.path.join(file_path, "output", "population.png")))
        self.assertTrue(os.path.exists(os.path.join(file_path, "output", "population.json")))
        self.assertTrue(os.path.exists(os.path.join(file_path, "WorkOrder.json")))

    def test_get_files_from_id(self):
        wi_id = '63b1822e-1e62-ea11-a2bf-f0921c167862'  # comps2 wi_id
        # wi_id = '5f7a43d8-6aed-ea11-941f-0050569e0ef3'  # idmtvapp17 wi_id
        out_filenames = ["output/population.png", "output/population.json", "WorkOrder.json"]
        ret = self.platform.get_files_by_id(wi_id, ItemType.WORKFLOW_ITEM, out_filenames)
        self.assertListEqual(list(ret.keys()), out_filenames)

    def test_get_files_from_id_output(self):
        wi_id = '63b1822e-1e62-ea11-a2bf-f0921c167862'  # comps2 wi_id
        # wi_id = '5f7a43d8-6aed-ea11-941f-0050569e0ef3'  # idmtvapp17 wi_id
        local_output_path = "output"
        out_filenames = ["output/population.png", "output/population.json", "WorkOrder.json"]
        self.platform.get_files_by_id(wi_id, ItemType.WORKFLOW_ITEM, out_filenames, local_output_path)

        file_path = os.path.join(local_output_path, str(wi_id))
        self.assertTrue(os.path.exists(os.path.join(file_path, "output", "population.png")))
        self.assertTrue(os.path.exists(os.path.join(file_path, "output", "population.json")))
        self.assertTrue(os.path.exists(os.path.join(file_path, "WorkOrder.json")))

    def test_csv_analyzer_analyze_work_item_output(self):
        # to COMPS's assets
        asset_files = FileList()
        asset_files.add_file(os.path.join(self.input_file_path, 'csv_analyzer.py'))
        asset_files.add_file(os.path.join(self.input_file_path, 'run_csv_analyzer.py'))

        # load local "input" folder simtools.ini to current dir in Comps workitem
        user_files = FileList()
        user_files.add_file(os.path.join(self.input_file_path, "idmtools.ini"))

        experiment_id = '9311af40-1337-ea11-a2be-f0921c167861'  # staging comps2 exp id
        # experiment_id = 'de07f612-69ed-ea11-941f-0050569e0ef3'  # idmtvapp17
        command = "python Assets/run_csv_analyzer.py " + experiment_id
        wi = SSMTWorkItem(item_name=self.case_name, command=command, asset_files=asset_files, user_files=user_files,
                          tags=self.tags)
        wi.run(wait_on_done=True)
        local_output_path = "output"
        out_filenames = ["output_csv/" + experiment_id + "/CSVAnalyzer.csv"]  # new
        # out_filenames = ["output_csv/CSVAnalyzer.csv"]  # old
        self.platform.get_files_by_id(wi.id, ItemType.WORKFLOW_ITEM, out_filenames, local_output_path)

        file_path = os.path.join(local_output_path, wi.id)
        self.assertTrue(os.path.exists(os.path.join(file_path, "output_csv", experiment_id, "CSVAnalyzer.csv")))  # new
        # self.assertTrue(os.path.exists(os.path.join(file_path, "output_csv", "CSVAnalyzer.csv")))  # old

        # analyze above finished workitem with Download analyzer
        local_output_path = "output"
        analyzers = [DownloadAnalyzer(filenames=out_filenames, output_path=local_output_path)]

        # Specify the id Type, in this case an WorkItem on COMPS
        manager = AnalyzeManager(ids=[(wi.uid, ItemType.WORKFLOW_ITEM)],
                                 analyzers=analyzers)
        # Analyze
        manager.analyze()

        # validate analyzer result.
        self.assertTrue(os.path.exists(os.path.join(local_output_path, wi.id, "CSVAnalyzer.csv")))

    def test_get_wi_with_query_criteria_1(self):
        wi_id = '5e2fc03d-2162-ea11-a2bf-f0921c167862'  # comps2 wi_id
        # wi_id = '5f7a43d8-6aed-ea11-941f-0050569e0ef3'  # idmtvapp17 wi_id

        cols = ["id", "name", "asset_collection_id"]
        children = ["tags", "files"]

        wi = self.platform.get_item(wi_id, ItemType.WORKFLOW_ITEM, columns=cols, load_children=children)
        self.assertIsNotNone(wi.item_name)
        self.assertIsNotNone(wi.asset_collection_id)
        self.assertIsNotNone(wi.tags)
        self.assertIsNotNone(wi.user_files)

    def test_get_wi_with_query_criteria_2(self):
        wi_id = '5e2fc03d-2162-ea11-a2bf-f0921c167862'  # comps2 wi_id
        # wi_id = '5f7a43d8-6aed-ea11-941f-0050569e0ef3'  # idmtvapp17 wi_id
        cols = ["id", "name"]
        children = []

        wi = self.platform.get_item(wi_id, ItemType.WORKFLOW_ITEM, columns=cols, load_children=children)
        self.assertIsNone(wi.asset_collection_id)
        self.assertIsNone(wi.tags)
        self.assertIsNone(wi.user_files)
