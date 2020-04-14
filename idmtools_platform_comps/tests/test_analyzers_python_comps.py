import os
import sys
from functools import partial

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
from idmtools_test.utils.utils import del_folder

current_directory = os.path.dirname(os.path.realpath(__file__))

# import analyzers from current dir's inputs dir
analyzer_path = os.path.join(os.path.dirname(__file__), "inputs")
sys.path.insert(0, analyzer_path)
from sim_filter_analyzer import SimFilterAnalyzer  # noqa
from sim_filter_analyzer_by_id import SimFilterAnalyzerById  # noqa


@pytest.mark.analysis
@pytest.mark.python
@pytest.mark.comps
class TestAnalyzeManagerPythonComps(ITestWithPersistence):

    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        print(self.case_name)
        self.p = Platform('COMPS2')

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

        wait_on_experiment_and_check_all_sim_status(self, pe, self.p)
        experiment = COMPSExperiment.get(pe.uid)
        print(experiment.id)
        self.exp_id = experiment.id  # COMPS Experiment object, so .id

        # Uncomment out if you do not want to regenerate exp and sims
        # self.exp_id = '9eacbb9a-5ecf-e911-a2bb-f0921c167866' #comps2 staging

    @pytest.mark.long
    def test_download_analyzer(self):
        # delete output from previous run
        del_folder("output")

        # create a new empty 'output' dir
        os.mkdir("output")
        self.create_experiment()
        filenames = ['output/result.json', 'config.json']
        analyzers = [DownloadAnalyzer(filenames=filenames, output_path='output')]

        am = AnalyzeManager(platform=self.p, ids=[(self.exp_id, ItemType.EXPERIMENT)], analyzers=analyzers)
        am.analyze()

        for simulation in COMPSExperiment.get(self.exp_id).get_simulations():
            self.assertTrue(os.path.exists(os.path.join('output', str(simulation.id), "config.json")))
            self.assertTrue(os.path.exists(os.path.join('output', str(simulation.id), "result.json")))

    def test_analyzer_multiple_experiments(self):
        # delete output from previous run
        del_folder("output")

        # create a new empty 'output' dir
        os.mkdir("output")

        filenames = ['output/result.json', 'config.json']
        analyzers = [DownloadAnalyzer(filenames=filenames, output_path='output')]

        exp_list = [('3ca4491a-0edb-e911-a2be-f0921c167861', ItemType.EXPERIMENT),
                    ('4dcd7149-4eda-e911-a2be-f0921c167861', ItemType.EXPERIMENT)]

        am = AnalyzeManager(platform=self.p, ids=exp_list, analyzers=analyzers)
        am.analyze()
        for exp_id in exp_list:
            for simulation in COMPSExperiment.get(exp_id[0]).get_simulations():
                self.assertTrue(os.path.exists(os.path.join('output', str(simulation.id), "config.json")))
                self.assertTrue(os.path.exists(os.path.join('output', str(simulation.id), "result.json")))

    def test_analyzer_filter_sims(self):
        # delete output from previous run
        del_folder("output")

        # create a new empty 'output' dir
        os.mkdir("output")

        exp_id = '69cab2fe-a252-ea11-a2bf-f0921c167862'

        # then run SimFilterAnalyzer to analyze the sims tags
        filenames = ['output/result.json']
        analyzers = [SimFilterAnalyzer(filenames=filenames, output_path='output')]

        am = AnalyzeManager(platform=self.p, ids=[(exp_id, ItemType.EXPERIMENT)], analyzers=analyzers)
        am.analyze()

        # validate result
        file_path = os.path.join("output", "b_match.csv")
        self.assertTrue(os.path.exists(file_path))
        df = pd.read_csv(file_path, names=['index', 'key', 'value'], header=None)
        self.assertTrue(df['key'].values[1:5].size == 4)
        self.assertTrue(df['key'].values[1:5].all() == 'b')
        self.assertTrue(df['value'].values[1:5].size == 4)
        self.assertTrue(df['value'].values[1:5].all() == '2')

    def test_analyzer_filter_sims_by_id(self):
        # delete output from previous run
        del_folder("output")

        # create a new empty 'output' dir
        os.mkdir("output")

        exp_id = '69cab2fe-a252-ea11-a2bf-f0921c167862'

        # then run SimFilterAnalyzer to analyze the sims tags
        filenames = ['output/result.json']
        analyzers = [SimFilterAnalyzerById(filenames=filenames, output_path='output')]

        am = AnalyzeManager(platform=self.p, ids=[(exp_id, ItemType.EXPERIMENT)], analyzers=analyzers)
        am.analyze()

        # validate result
        file_path = os.path.join("output", "result.csv")
        self.assertTrue(os.path.exists(file_path))
        # validate content of output.csv
        df = pd.read_csv(file_path, names=['SimId', 'a', 'b', 'c'], header=None)
        self.assertTrue(df['SimId'].values[1:7].size == 6)
        self.assertTrue(df['a'].values[1:7].size == 6)
        self.assertTrue(df['b'].values[1:7].size == 6)
        self.assertTrue(df['c'].values[1:7].size == 6)

    # test analyzer with parameter: analyze_failed_items=True
    # note: when this flag to True, it does not mean analyzer only on failed simulations, it also on succeeded sims
    def test_analyzer_with_failed_sims(self):
        experiment_id = 'c3e4ef50-ee63-ea11-a2bf-f0921c167862'  # staging experiment includes 5 sims with 3 failed sims

        # delete output from previous run
        output_dir = "output"
        del_folder(output_dir)
        filenames = ["stdErr.txt"]
        analyzers = [DownloadAnalyzer(filenames=filenames)]
        manager = AnalyzeManager(platform=self.p, partial_analyze_ok=False,
                                 ids=[(experiment_id, ItemType.EXPERIMENT)],
                                 analyzers=analyzers, analyze_failed_items=True)
        manager.analyze()

        # validation
        for simulation in self.p.get_children(experiment_id, ItemType.EXPERIMENT):
            file = os.path.join("output", str(simulation.id), "stdErr.txt")
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
    def test_analyzer_with_succeeded_sims(self):
        experiment_id = 'c3e4ef50-ee63-ea11-a2bf-f0921c167862'  # staging experiment includes 5 sims with 3 failed sims

        # delete output from previous run
        output_dir = "output"
        del_folder(output_dir)
        filenames = ["stdOut.txt"]
        analyzers = [DownloadAnalyzer(filenames=filenames)]
        manager = AnalyzeManager(platform=self.p, partial_analyze_ok=True,
                                 ids=[(experiment_id, ItemType.EXPERIMENT)],
                                 analyzers=analyzers)
        manager.analyze()

        # validation
        for simulation in self.p.get_children(experiment_id, ItemType.EXPERIMENT):
            if simulation.id == "c7e4ef50-ee63-ea11-a2bf-f0921c167862" \
                    or simulation.id == "c5e4ef50-ee63-ea11-a2bf-f0921c167862":
                file = os.path.join("output", str(simulation.id), "stdOut.txt")
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
                file = os.path.join("output", str(simulation.id), "stdOut.txt")
                self.assertFalse(os.path.exists(file))
