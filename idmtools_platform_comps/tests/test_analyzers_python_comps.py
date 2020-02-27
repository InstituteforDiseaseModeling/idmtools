import os
import sys
from functools import partial

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
from SimFilterAnalyzer import SimFilterAnalyzer


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
    def test_DownloadAnalyzer(self):
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

        platform = Platform('COMPS2')
        am = AnalyzeManager(platform=platform, ids=[(exp_id, ItemType.EXPERIMENT)], analyzers=analyzers)
        am.analyze()

        for simulation in COMPSExperiment.get(exp_id).get_simulations():
            # verify results
            self.assertTrue(os.path.exists(os.path.join("output", "b_match.csv")))
