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
from idmtools.assets import AssetCollection
from idmtools.builders import ExperimentBuilder
from idmtools_models.python import PythonExperiment
from COMPS.Data import Experiment
from idmtools.managers import ExperimentManager
from idmtools.core import EntityStatus, ItemType
from functools import partial
from idmtools_test import COMMON_INPUT_PATH

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
        analysis = SSMTAnalysis(platform=self.platform,
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
                         "python analyze_ssmt.py " + experiment_id + " SimpleAnalyzer.SimpleAnalyzer")

    # Test CSVAnalyzer with SSMTAnalysis which analyzes python experiment's results
    def test_ssmt_workitem_python_csv_analyzer(self):
        sys.path.insert(0, self.input_file_path)
        from CSVAnalyzer import CSVAnalyzer
        experiment_id = "9311af40-1337-ea11-a2be-f0921c167861"
        analysis = SSMTAnalysis(platform=self.platform,
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
                         "python analyze_ssmt.py " + experiment_id + " CSVAnalyzer.CSVAnalyzer COMPS2")

    # test SSMTWorkItem where waiting for sims to complete first
    @pytest.mark.long
    @pytest.mark.comps
    # TODO: won't work until merge Ye's SEIR model
    # def test_ssmt_workitem_waiting_for_sims_to_finish(self):
    def test_ssmt_seir_model_analysis(self):
        # ------------------------------------------------------
        # First run the experiment
        # ------------------------------------------------------
        # Create the asset collection for experiment
        ac = AssetCollection()
        assets_path = os.path.join(COMMON_INPUT_PATH, "python", "ye_seir_model", "Assets")
        ac.add_directory(assets_directory=assets_path)
        # TODO: Refactor once refactor model to task is merged
        pe = PythonExperiment(name=self.case_name,
                              model_path=os.path.join(COMMON_INPUT_PATH, "python", "ye_seir_model", "Assets", "SEIR_model.py"),
                              assets=ac)
        pe.tags = {"idmtools": "idmtools-automation", "simulation_name_tag": "SEIR_Model"}
        builder = ExperimentBuilder()
        # ------------------------------------------------------
        # Sweep parameters

        # utility function to update parameters
        def param_update(simulation, param, value):
            return simulation.set_parameter(param, value)

        set_base_infectivity_gaussian_mean = partial(param_update,
                                                     param=ConfigParameters.Base_Infectivity_Gaussian_Mean)

        builder.add_sweep_definition(set_base_infectivity_gaussian_mean, [0.5, 2])

        pe.builder = builder

        em = ExperimentManager(experiment=pe, platform=self.platform)
        em.run()
        em.wait_till_done()
        self.assertTrue(all([s.status == EntityStatus.SUCCEEDED for s in pe.simulations]))
        experiment = Experiment.get(em.experiment.uid)
        print(experiment.id)
        exp_id = experiment.id

        # ------------------------------------------------------
        # Run analyzers
        # To just test the analyzer, uncomment this
        sys.path.insert(0, self.input_file_path)
        experiment_id = "9311af40-1337-ea11-a2be-f0921c167861"
        from InfectiousnessCSVAnalyzer import InfectiousnessCSVAnalyzer
        # from NodeCSVAnalyzer import NodeCSVAnalyzer
        filenames = ['output/individual.csv']
        # filenames_2 = ['output/node.csv']
        analysis = SSMTAnalysis(platform=self.platform,
                                experiment_ids=[experiment_id],
                                # analyzers=[InfectiousnessCSVAnalyzer(filenames=filenames),
                                #            NodeCSVAnalyzer(filenames=filenames_2)],
                                analyzers=[InfectiousnessCSVAnalyzer],
                                # analyzers_args=[{'filenames': ['output/individual.csv']},
                                #                 {'filenames': ['output/node.csv']}],
                                analyzers_args=[{'filenames': ['output/individual.csv']}],
                                analysis_name=self.case_name,
                                tags={'idmtools': self._testMethodName, 'WorkItem type': 'Docker'})

        analysis.analyze(check_status=True)
        wi = analysis.get_work_item()

        # Verify workitem results
        local_output_path = "output"
        del_folder(local_output_path)
        out_filenames = ["output/individual.csv", "output/node.csv"]
        ret = self.platform.get_files_by_id(wi.uid, ItemType.WORKFLOW_ITEM, out_filenames, local_output_path)

        file_path = os.path.join(local_output_path, str(wi.uid))
        self.assertTrue(os.path.exists(os.path.join(file_path, "output", "individual.csv")))
        self.assertTrue(os.path.exists(os.path.join(file_path, "output", "node.csv")))
        # worker_order = json.load(open(os.path.join(file_path, "WorkOrder.json"), 'r'))
        # print(worker_order)
        # self.assertEqual(worker_order['WorkItem_Type'], "DockerWorker")
        # execution = worker_order['Execution']
        # self.assertEqual(execution['Command'],
        #                  "python custom_csv_analyzer.py " + exp_id + " SimpleAnalyzer.SimpleAnalyzer")


# Define some constant string used in this example
class ConfigParameters():
    Infectious_Period_Constant = "Infectious_Period_Constant"
    Base_Infectivity_Constant = "Base_Infectivity_Constant"
    Base_Infectivity_Distribution = "Base_Infectivity_Distribution"
    GAUSSIAN_DISTRIBUTION = "GAUSSIAN_DISTRIBUTION"
    Base_Infectivity_Gaussian_Mean = "Base_Infectivity_Gaussian_Mean"
    Base_Infectivity_Gaussian_Std_Dev = "Base_Infectivity_Gaussian_Std_Dev"