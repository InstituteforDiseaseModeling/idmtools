import allure
import os
import sys
from functools import partial

import numpy as np
import pandas as pd
import pytest
from COMPS.Data import Experiment as COMPSExperiment
from idmtools.analysis.analyze_manager import AnalyzeManager
from idmtools.analysis.download_analyzer import DownloadAnalyzer
from idmtools.builders import SimulationBuilder
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools_test.utils.common_experiments import wait_on_experiment_and_check_all_sim_status, \
    get_model1_templated_experiment
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools_test.utils.utils import del_folder, get_case_name
from idmtools_test.utils.decorators import run_in_temp_dir

current_directory = os.path.dirname(os.path.realpath(__file__))

# import analyzers from current dir's inputs dir
analyzer_path = os.path.join(os.path.dirname(__file__), "inputs")
sys.path.insert(0, analyzer_path)
from sim_filter_analyzer import SimFilterAnalyzer

@pytest.mark.analysis
@pytest.mark.python
@pytest.mark.comps
@allure.story("COMPS")
@allure.story("Analyzers")
@allure.suite("idmtools_platform_comps")
class TestAnalyzeManagerPythonComps(ITestWithPersistence):

    def setUp(self) -> None:
        self.case_name = get_case_name(os.path.basename(__file__) + "--" + self._testMethodName)
        print(self.case_name)
        self.platform = Platform('SlurmStage')

    def create_experiment(self):
        pe = get_model1_templated_experiment(self.case_name)

        def param_update_ab(simulation, param, value):
            # Set B within
            if param == "a":
                simulation.task.set_parameter("b", value + 2)

            return simulation.task.set_parameter(param, value)

        setAB = partial(param_update_ab, param="a")

        builder = SimulationBuilder()
        # Sweep parameter "a" and make "b" depends on "a"
        builder.add_sweep_definition(setAB, range(0, 2))
        pe.simulations.add_builder(builder)

        wait_on_experiment_and_check_all_sim_status(self, pe)
        experiment = COMPSExperiment.get(pe.uid)
        print(experiment.id)
        exp_id = experiment.id  # COMPS Experiment object, so .id

        # Uncomment out if you do not want to regenerate exp and sims
        # exp_id = '9eacbb9a-5ecf-e911-a2bb-f0921c167866' #comps2 staging
        return exp_id

    @pytest.mark.long
    @pytest.mark.serial
    @run_in_temp_dir
    def test_download_analyzer(self):
        # step1: test with 1 experiment
        output_folder = "output_test_download_analyzer"
        exp_id1 = self.create_experiment()
        filenames = ['output/result.json', 'config.json']
        analyzers = [DownloadAnalyzer(filenames=filenames, output_path=output_folder)]

        am = AnalyzeManager(ids=[(exp_id1, ItemType.EXPERIMENT)], analyzers=analyzers)
        am.analyze()
        for simulation in COMPSExperiment.get(exp_id1).get_simulations():
            self.assertTrue(os.path.exists(os.path.join(output_folder, str(simulation.id), "config.json")))
            self.assertTrue(os.path.exists(os.path.join(output_folder, str(simulation.id), "result.json")))

        # step2: test with 2 experiments
        exp_id2 = self.create_experiment()
        exp_list = [(exp_id1, ItemType.EXPERIMENT),
                    (exp_id2, ItemType.EXPERIMENT)]
        output_folder = "output_test_download_analyzer1"
        del_folder(output_folder)
        analyzers = [DownloadAnalyzer(filenames=filenames, output_path=output_folder)]
        am = AnalyzeManager(ids=exp_list, analyzers=analyzers)
        am.analyze()
        for exp_id in exp_list:
            for simulation in COMPSExperiment.get(exp_id[0]).get_simulations():
                self.assertTrue(os.path.exists(os.path.join(output_folder, str(simulation.id), "config.json")))
                self.assertTrue(os.path.exists(os.path.join(output_folder, str(simulation.id), "result.json")))

    @pytest.mark.serial
    @run_in_temp_dir
    def test_analyzer_filter_sims(self):
        exp_id = '69cab2fe-a252-ea11-a2bf-f0921c167862'  # comps2
        # then run SimFilterAnalyzer to analyze the sims tags
        filenames = ['output/result.json']
        output_folder = "output_test_analyzer_filter_sims"
        analyzers = [SimFilterAnalyzer(filenames=filenames, output_path=output_folder)]

        am = AnalyzeManager(ids=[(exp_id, ItemType.EXPERIMENT)], analyzers=analyzers)
        am.analyze()

        # validate result
        file_path = os.path.join(output_folder, exp_id, "b_match.csv")
        self.assertTrue(os.path.exists(file_path))
        df = pd.read_csv(file_path, names=['index', 'key', 'value'], header=None)
        self.assertTrue(df['key'].values[1:5].size == 4)
        self.assertTrue(np.all(df['key'].values[1:5] == 'b'))
        self.assertTrue(df['value'].values[1:5].size == 4)
        self.assertTrue(np.all(df['value'].values[1:5] == '2'))

    @pytest.mark.serial
    @run_in_temp_dir
    def test_analyzer_filter_sims_by_id(self):
        exp_id = '69cab2fe-a252-ea11-a2bf-f0921c167862'  # comps2
        output_folder = "output_test_analyzer_filter_sims_by_id"
        # then run SimFilterAnalyzer to analyze the sims tags
        filenames = ['output/result.json']
        from sim_filter_analyzer_by_id import SimFilterAnalyzerById  # noqa
        analyzers = [SimFilterAnalyzerById(filenames=filenames, output_path=output_folder)]

        am = AnalyzeManager(ids=[(exp_id, ItemType.EXPERIMENT)], analyzers=analyzers)
        am.analyze()

        # validate result
        file_path = os.path.join(output_folder, exp_id, "result.csv")
        self.assertTrue(os.path.exists(file_path))
        # validate content of output.csv
        df = pd.read_csv(file_path, names=['SimId', 'a', 'b', 'c'], header=None)
        self.assertTrue(df['SimId'].values[1:7].size == 6)
        self.assertTrue(df['a'].values[1:7].size == 6)
        self.assertTrue(df['b'].values[1:7].size == 6)
        self.assertTrue(df['c'].values[1:7].size == 6)

    # test analyzer with parameter: analyze_failed_items=True
    # note: when this flag to True, it does not mean analyzer only on failed simulations, it also on succeeded sims
    @pytest.mark.serial
    @run_in_temp_dir
    def test_analyzer_with_failed_sims(self):
        experiment_id = 'c3e4ef50-ee63-ea11-a2bf-f0921c167862'  # staging experiment includes 5 sims with 3 failed sims
        filenames = ["stdErr.txt"]
        output_folder = "output_test_analyzer_with_failed_sims"
        analyzers = [DownloadAnalyzer(filenames=filenames, output_path=output_folder)]
        manager = AnalyzeManager(ids=[(experiment_id, ItemType.EXPERIMENT)],
                                 analyzers=analyzers, analyze_failed_items=True)
        manager.analyze()

        # validation
        for simulation in self.platform.get_children(experiment_id, ItemType.EXPERIMENT):
            file = os.path.join(output_folder, str(simulation.id), "stdErr.txt")
            # make sure we have download all stdErr.txt files from all sims including failed ones
            self.assertTrue(os.path.exists(file))
            # make sure download analyzer results are correct
            # read 'output/stdErr.txt' file content
            contents = ""
            with open(file) as f:
                for line in f.readlines():
                    contents += line
            # for failed simulations, check stdErr.txt file content
            if simulation.id == "c6e4ef50-ee63-ea11-a2bf-f0921c167862" \
                    or simulation.id == "c8e4ef50-ee63-ea11-a2bf-f0921c167862" \
                    or simulation.id == "c4e4ef50-ee63-ea11-a2bf-f0921c167862":
                self.assertIn("Traceback (most recent call last)", contents)
            # for successful simulations, make sure stdErr.txt is empty
            else:
                self.assertEqual("", contents)

    # test analyzer with only succeeded simulations
    # note: experiment can have failed sims, but analyzer only analyzes succeeded sims
    @pytest.mark.smoke
    @pytest.mark.serial
    @run_in_temp_dir
    def test_analyzer_with_succeeded_sims(self):
        experiment_id = 'c3e4ef50-ee63-ea11-a2bf-f0921c167862'  # staging experiment includes 5 sims with 3 failed sims
        output_folder = "output_test_analyzer_with_succeeded_sims"

        filenames = ["stdOut.txt"]
        analyzers = [DownloadAnalyzer(filenames=filenames, output_path=output_folder)]
        manager = AnalyzeManager(partial_analyze_ok=True,
                                 ids=[(experiment_id, ItemType.EXPERIMENT)],
                                 analyzers=analyzers)
        manager.analyze()

        # validation
        for simulation in self.platform.get_children(experiment_id, ItemType.EXPERIMENT):
            if simulation.id == "c7e4ef50-ee63-ea11-a2bf-f0921c167862" \
                    or simulation.id == "c5e4ef50-ee63-ea11-a2bf-f0921c167862":
                file = os.path.join(output_folder, str(simulation.id), "stdOut.txt")
                # make sure DownloadAnalyzer only download succeeded simulation's stdOut.txt files
                self.assertTrue(os.path.exists(file))
                # make sure download analyzer results are correct
                # read 'output/stdOut.txt' file content
                contents = ""
                with open(file) as f:
                    for line in f.readlines():
                        contents += line
                # for succeeded simulations, check stdOut.txt file content
                self.assertIn("Done", contents)
            # for failed simulations, make sure there is no strOut.txt downloaded in local dir
            else:
                file = os.path.join(output_folder, str(simulation.id), "stdOut.txt")
                self.assertFalse(os.path.exists(file))

    @run_in_temp_dir
    def test_analyzer_with_scheduling_experiment(self):
        # files to download
        filenames = ['outputs/results.xlsx', 'outputs/results.json', 'WorkOrder.json']
        output_folder = "output_test_analyzer_with_scheduling_experiment"
        # Initialize the analyser class with the path of the output files to download
        analyzers = [DownloadAnalyzer(filenames=filenames, output_path=output_folder)]

        # experiment we use is from sheduling test in comps2
        experiment_id = 'acd2f035-b098-eb11-a2c4-f0921c167864'  # comps2 exp id

        manager = AnalyzeManager(ids=[(experiment_id, ItemType.EXPERIMENT)],
                                 analyzers=analyzers)
        manager.analyze()

        # verify download success
        for simulation in self.platform.get_children(experiment_id, ItemType.EXPERIMENT):
            path, dirs, files = next(os.walk(os.path.join(output_folder, str(simulation.id))))
            self.assertEqual(set(files), {'WorkOrder.json', 'results.xlsx', 'results.json'})

    def test_analyzer_manager_add_item_exp(self):
        exp_id = '69cab2fe-a252-ea11-a2bf-f0921c167862'  # comps2
        filenames = ['output/result.json']
        output_folder = self._testMethodName
        analyzers = [SimFilterAnalyzer(filenames=filenames, output_path=output_folder, result_file_name="match.csv")]
        exp = self.platform.get_item(item_id=exp_id, item_type=ItemType.EXPERIMENT)
        manager = AnalyzeManager(analyzers=analyzers)
        manager.add_item(exp)
        manager.analyze()
        file_path = os.path.join(output_folder, exp_id, "match.csv")
        self.assertTrue(os.path.exists(file_path))
        df = pd.read_csv(file_path)
        assert (df['tags'] == 'b').all()
        assert (df['value'] == 2).all()
        self.assertEqual((df['tags'] == 'b').sum(), 4)  # total 4 simulations match tag b=2

    def test_analyzer_manager_add_item_exp_raw_true(self):
        exp_id = '69cab2fe-a252-ea11-a2bf-f0921c167862'  # comps2
        filenames = ['output/result.json']
        output_folder = self._testMethodName
        analyzers = [SimFilterAnalyzer(filenames=filenames, output_path=output_folder, result_file_name="match_true.csv")]
        exp = self.platform.get_item(item_id=exp_id, item_type=ItemType.EXPERIMENT, raw=True)
        manager = AnalyzeManager(analyzers=analyzers)
        manager.add_item(exp)
        manager.analyze()
        file_path = os.path.join(output_folder, exp_id, "match_true.csv")
        self.assertTrue(os.path.exists(file_path))
        df = pd.read_csv(file_path)
        assert (df['tags'] == 'b').all()
        assert (df['value'] == 2).all()
        self.assertEqual((df['tags'] == 'b').sum(), 4)  # total 4 simulations match tag b=2

    def test_analyzer_manager_suite(self):
        suite_id = 'c47cbc8c-e43c-f011-9310-f0921c167864'  # comps2
        filenames = ['config.json']
        analyzers = [DownloadAnalyzer(filenames=filenames, output_path=self._testMethodName)]
        manager = AnalyzeManager(analyzers=analyzers, ids=[(suite_id, ItemType.SUITE)], partial_analyze_ok=True)
        manager.analyze()
        expected_sims = ['c97cbc8c-e43c-f011-9310-f0921c167864', 'c77cbc8c-e43c-f011-9310-f0921c167864']
        for sim_id in expected_sims:
            path, dirs, files = next(os.walk(os.path.join(self._testMethodName, sim_id)))
            self.assertEqual(set(files), {"config.json"})

    def test_analyzer_manager_add_item_suite(self):
        suite_id = 'c47cbc8c-e43c-f011-9310-f0921c167864'
        suite = self.platform.get_item(item_id=suite_id, item_type=ItemType.SUITE, raw=True)
        filenames = ['config.json']
        analyzers = [DownloadAnalyzer(filenames=filenames, output_path=self._testMethodName)]
        manager = AnalyzeManager(analyzers=analyzers, partial_analyze_ok=True)
        manager.add_item(suite)
        manager.analyze()
        expected_sims = ['c97cbc8c-e43c-f011-9310-f0921c167864', 'c77cbc8c-e43c-f011-9310-f0921c167864']
        for sim_id in expected_sims:
            path, dirs, files = next(os.walk(os.path.join(self._testMethodName, sim_id)))
            self.assertEqual(set(files), {"config.json"})

    def test_analyzer_manager_exp(self):
        exp_id = '69cab2fe-a252-ea11-a2bf-f0921c167862'  # comps2
        filenames = ['output/result.json']
        output_folder = self._testMethodName
        analyzers = [SimFilterAnalyzer(filenames=filenames, output_path=output_folder, result_file_name="match_exp.csv")]
        manager = AnalyzeManager(analyzers=analyzers, ids=[(exp_id, ItemType.EXPERIMENT)])
        manager.analyze()
        file_path = os.path.join(output_folder, exp_id, "match_exp.csv")
        self.assertTrue(os.path.exists(file_path))
        df = pd.read_csv(file_path)
        assert (df['tags'] == 'b').all()
        assert (df['value'] == 2).all()
        self.assertEqual((df['tags'] == 'b').sum(), 4)  # total 4 simulations match tag b=2

    def test_analyzer_manager_add_item_sims(self):
        sim_id1 = '6fcab2fe-a252-ea11-a2bf-f0921c167862'
        sim_id2 = '6ecab2fe-a252-ea11-a2bf-f0921c167862'
        sim_id3 = '6dcab2fe-a252-ea11-a2bf-f0921c167862'
        sim_id4 = '6ccab2fe-a252-ea11-a2bf-f0921c167862'
        filenames = ['output/result.json']
        output_folder = self._testMethodName
        analyzers = [SimFilterAnalyzer(filenames=filenames, output_path=output_folder, result_file_name="match_sims.csv")]
        sim1 = self.platform.get_item(item_id=sim_id1, item_type=ItemType.SIMULATION)
        sim2 = self.platform.get_item(item_id=sim_id2, item_type=ItemType.SIMULATION)
        sim3 = self.platform.get_item(item_id=sim_id3, item_type=ItemType.SIMULATION, raw=True)
        sim4 = self.platform.get_item(item_id=sim_id4, item_type=ItemType.SIMULATION)
        manager = AnalyzeManager(analyzers=analyzers)
        manager.add_item(sim1)
        manager.add_item(sim2)
        manager.add_item(sim3)
        manager.add_item(sim4)
        manager.analyze()
        file_path = os.path.join(output_folder, sim1.experiment.id, "match_sims.csv")
        self.assertTrue(os.path.exists(file_path))
        df = pd.read_csv(file_path)
        self.assertEqual((df['tags'] == 'b').sum(), 2)  # total 2 simulations match tag b=2
        matched_sim_id_list = [sim_id1, sim_id2]
        assert df['sim_id'].isin(matched_sim_id_list).all()