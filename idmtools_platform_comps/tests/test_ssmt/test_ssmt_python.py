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
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools.builders import SimulationBuilder
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from COMPS.Data import Experiment
from idmtools.core import EntityStatus, ItemType
from functools import partial
from idmtools_test import COMMON_INPUT_PATH


# import analyzers from current dir's inputs dir
analyzer_path = os.path.join(os.path.dirname(__file__), "..", "inputs")
sys.path.insert(0, analyzer_path)
from SimpleAnalyzer import SimpleAnalyzer  # noqa
from CSVAnalyzer import CSVAnalyzer  # noqa


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
        wi.run(True, platform=self.platform)

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
                         "python platform_analysis_bootstrap.py " + experiment_id + " SimpleAnalyzer.SimpleAnalyzer comps2")

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
                         "python platform_analysis_bootstrap.py " + experiment_id + " CSVAnalyzer.CSVAnalyzer comps2")

    # test SSMTWorkItem where waiting for sims to complete first
    @pytest.mark.long
    @pytest.mark.comps
    # TODO: won't work until merge Ye's SEIR model
    # def test_ssmt_workitem_waiting_for_sims_to_finish(self):
    def test_ssmt_seir_model_analysis(self):
        # ------------------------------------------------------
        # First run the experiment
        # ------------------------------------------------------
        script_path = os.path.join(COMMON_INPUT_PATH, "python", "ye_seir_model", "Assets", "SEIR_model.py")
        assets_path = os.path.join(COMMON_INPUT_PATH, "python", "ye_seir_model", "Assets")
        tags = {"idmtools": "idmtools-automation", "simulation_name_tag": "SEIR_Model"}

        parameters = json.load(open(os.path.join(assets_path, 'config.json'), 'r'))
        parameters[ConfigParameters.Base_Infectivity_Distribution] = ConfigParameters.GAUSSIAN_DISTRIBUTION
        task = JSONConfiguredPythonTask(name=self.case_name,
                                        script_path=script_path, parameters=parameters, config_file_name='config.json')
        task.command.add_option("--duration", 40)

        # now create a TemplatedSimulation builder
        ts = TemplatedSimulations(base_task=task)
        ts.base_simulation.tags = tags

        # now define our sweeps
        builder = SimulationBuilder()

        # utility function to update parameters
        def param_update(simulation, param, value):
            return simulation.set_parameter(param, value)

        set_base_infectivity_gaussian_mean = partial(param_update,
                                                     param=ConfigParameters.Base_Infectivity_Gaussian_Mean)

        builder.add_sweep_definition(set_base_infectivity_gaussian_mean, [0.5, 2])

        ts.add_builder(builder)

        # now we can create our experiment using our template builder
        experiment = Experiment(name=, simulations=ts)
        experiment.tags = tags

        # add the asset collection for experiment
        experiment.assets.add_directory(assets_directory=assets_path)

        # set platform and run simulations
        platform = Platform('COMPS2')
        platform.run()
        platform.wait_till_done()

        # check experiment status and only move to analyzer test if experiment succeeded
        if not experiment.succeeded:
            print(f"Experiment {experiment.uid} failed.\n")
            sys.exit(-1)

        # set the exp_id for the analyzer test
        exp_id = experiment.id

        # ------------------------------------------------------
        # Run analyzers
        # To just test the analyzer, comment out exp creation and uncomment this exp id
        # exp_id = '9311af40-1337-ea11-a2be-f0921c167861'  # comps2 staging exp id
        sys.path.insert(0, self.input_file_path)
        from InfectiousnessCSVAnalyzer import InfectiousnessCSVAnalyzer
        from NodeCSVAnalyzer import NodeCSVAnalyzer
        filenames = ['output/individual.csv']
        filenames_2 = ['output/node.csv']
        analysis = PlatformAnalysis(platform=self.platform,
                                experiment_ids=[exp_id],
                                analyzers=[InfectiousnessCSVAnalyzer(filenames=filenames),
                                           NodeCSVAnalyzer(filenames=filenames_2)],
                                analyzers_args=[{'filenames': filenames}],
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
        worker_order = json.load(open(os.path.join(file_path, "WorkOrder.json"), 'r'))
        print(worker_order)
        self.assertEqual(worker_order['WorkItem_Type'], "DockerWorker")
        execution = worker_order['Execution']
        self.assertEqual(execution['Command'],
                         "python platform_analysis_bootstrap.py " + exp_id + " InfectiousnessCSVAnalyzer.InfectiousnessCSVAnalyzer, NodeCSVAnalyzer.NodeCSVAnalyzer comps2")


# Define some constant string used in this example
class ConfigParameters:
    Infectious_Period_Constant = "Infectious_Period_Constant"
    Base_Infectivity_Constant = "Base_Infectivity_Constant"
    Base_Infectivity_Distribution = "Base_Infectivity_Distribution"
    GAUSSIAN_DISTRIBUTION = "GAUSSIAN_DISTRIBUTION"
    Base_Infectivity_Gaussian_Mean = "Base_Infectivity_Gaussian_Mean"
    Base_Infectivity_Gaussian_Std_Dev = "Base_Infectivity_Gaussian_Std_Dev"
