import json
import os
import sys
from functools import partial

import pytest
from COMPS.Data import Experiment

from idmtools.analysis.add_analyzer import AddAnalyzer
from idmtools.analysis.analyze_manager import AnalyzeManager
from idmtools.analysis.download_analyzer import DownloadAnalyzer
from idmtools.builders import ExperimentBuilder
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.managers import ExperimentManager
from idmtools_model_emod.defaults import EMODSir
from idmtools_model_emod.emod_experiment import EMODExperiment
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools_test.utils.utils import del_file, del_folder, load_csv_file

current_directory = os.path.dirname(os.path.realpath(__file__))


def param_update(simulation, param, value):
    return simulation.set_parameter(param, value)


setA = partial(param_update, param="a")
setB = partial(param_update, param="b")
setC = partial(param_update, param="c")
setD = partial(param_update, param="d")


@pytest.mark.comps
@pytest.mark.analysis
class TestAnalyzeManagerEmodComps(ITestWithPersistence):

    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        print(self.case_name)
        self.p = Platform('COMPS2')

    def create_experiment(self):

        e = EMODExperiment.from_default(self.case_name, default=EMODSir(),
                                        eradication_path=os.path.join(COMMON_INPUT_PATH, "emod", "Eradication.exe"))
        e.tags = {"idmtools": "idmtools-automation", "string_tag": "test", "number_tag": 123}

        e.base_simulation.set_parameter("Enable_Immunity", 0)

        def param_a_update(simulation, value):
            simulation.set_parameter("Run_Number", value)
            return {"Run_Number": value}

        self.builder = ExperimentBuilder()
        # Sweep parameter "Run_Number"
        self.builder.add_sweep_definition(param_a_update, range(0, 2))
        e.builder = self.builder
        em = ExperimentManager(experiment=e, platform=self.p)
        em.run()
        em.wait_till_done()
        self.assertTrue(e.succeeded)
        self.exp_id = em.experiment.uid

        # Uncomment out if you do not want to regenerate exp and sims
        # self.exp_id = '9eacbb9a-5ecf-e911-a2bb-f0921c167866' #comps2 staging

    @pytest.mark.long
    def test_AddAnalyzer(self):

        self.create_experiment()

        filenames = ['StdOut.txt']
        analyzers = [AddAnalyzer(filenames=filenames)]

        am = AnalyzeManager(platform=self.p, ids=[(self.exp_id, ItemType.EXPERIMENT)], analyzers=analyzers)
        am.analyze()

    @pytest.mark.long
    def test_DownloadAnalyzer(self):
        # delete output from previous run
        del_folder("output")

        # create a new empty 'output' dir
        os.mkdir("output")

        self.create_experiment()

        filenames = ['output/InsetChart.json', 'config.json']
        analyzers = [DownloadAnalyzer(filenames=filenames, output_path='output')]

        am = AnalyzeManager(platform=self.p, ids=[(self.exp_id, ItemType.EXPERIMENT)], analyzers=analyzers)
        am.analyze()

        for simulation in Experiment.get(self.exp_id).get_simulations():
            s = simulation.get(id=simulation.id)
            self.assertTrue(os.path.exists(os.path.join('output', str(s.id), "config.json")))
            self.assertTrue(os.path.exists(os.path.join('output', str(s.id), "InsetChart.json")))

    def test_analyzer_multiple_experiments(self):
        # delete output from previous run
        del_folder("output")

        # create a new empty 'output' dir
        os.mkdir("output")

        filenames = ['output/InsetChart.json', 'config.json']
        analyzers = [DownloadAnalyzer(filenames=filenames, output_path='output')]

        exp_list = [('6f693627-6de5-e911-a2be-f0921c167861', ItemType.EXPERIMENT),
                    ('1991ec0d-6ce5-e911-a2be-f0921c167861', ItemType.EXPERIMENT)]  # comps2 staging
        am = AnalyzeManager(platform=self.p, ids=exp_list, analyzers=analyzers)
        am.analyze()

    @pytest.mark.long
    def test_population_analyzer(self):
        analyzer_path = os.path.join(os.path.dirname(__file__), "inputs", "analyzers")
        del_file(os.path.join(analyzer_path, 'population.csv'))
        del_file(os.path.join(analyzer_path, 'population.png'))
        self.create_experiment()

        # self.exp_id = uuid.UUID("fc59240c-07db-e911-a2be-f0921c167861")
        filenames = ['output/InsetChart.json']


        sys.path.insert(0, analyzer_path)
        from PopulationAnalyzer import PopulationAnalyzer
        analyzers = [PopulationAnalyzer(filenames=filenames)]

        am = AnalyzeManager(platform=self.p, ids=[(self.exp_id, ItemType.EXPERIMENT)], analyzers=analyzers)
        am.analyze()

        # -----------------------------------------------------------------------------------------------------
        # Compare "Statistical Population" values in PopulationAnalyzer's output file: 'population.csv'
        # with COMPS's out\InsetChart.json for each simulation
        # -----------------------------------------------------------------------------------------------------
        df = load_csv_file(os.path.join(analyzer_path, 'population.csv'))
        sim_count = 1
        expected_sim_ids = []
        actual_sim_ids_in_comps = []
        for simulation in Experiment.get(self.exp_id).get_simulations():
            s = simulation.get(id=simulation.id)
            actual_sim_ids_in_comps.append(str(s.id))
            expected_sim_ids.append(df[1:2].iat[0, sim_count])

            insetchart_string = s.retrieve_output_files(paths=['output/InsetChart.json'])
            insetchart_dict = json.loads(insetchart_string[0].decode('utf-8'))
            population_data = insetchart_dict['Channels']['Statistical Population']['Data']
            # Validate every single Statistical Population' from insetChart.json are equals to population.csv file
            actual_population_data = []
            expected_population_data = []
            for i in range(0, len(population_data), 1):
                actual_population_data.append(str(population_data[i]))
                expected_population_data.append(df[2:].iloc[i, sim_count])
            self.assertEqual(sorted(actual_population_data), sorted(expected_population_data))
            sim_count = sim_count + 1
        self.assertSetEqual(set(actual_sim_ids_in_comps), set(expected_sim_ids))

    @pytest.mark.long
    def test_timeseries_analyzer_with_filter(self):
        analyzer_path = os.path.join(os.path.dirname(__file__), "inputs", "analyzers")
        del_file(os.path.join(analyzer_path, 'timeseries.csv'))
        del_file(os.path.join(analyzer_path, 'timeseries.png'))

        self.create_experiment()

        filenames = ['output/InsetChart.json']
        sys.path.insert(0, analyzer_path)
        from TimeseriesAnalyzer import TimeseriesAnalyzer

        analyzers = [TimeseriesAnalyzer(filenames=filenames)]

        # self.exp_id = uuid.UUID("fc59240c-07db-e911-a2be-f0921c167861")
        am = AnalyzeManager(platform=self.p, ids=[(self.exp_id, ItemType.EXPERIMENT)], analyzers=analyzers)
        am.analyze()

        # ------------------------------------------------------------------------------
        # Step3: Compare 'Adult Vector' channel in timeserier.csv and COMPS's out\InsetChart.json's 'Adult Vector'
        # ------------------------------------------------------------------------------
        df = load_csv_file(os.path.join(analyzer_path, 'timeseries.csv'))
        sim_count = 1
        expected_sim_ids = []
        actual_sim_ids_in_comps = []
        for simulation in Experiment.get(self.exp_id).get_simulations():
            s = simulation.get(id=simulation.id)
            actual_sim_ids_in_comps.append(str(s.id))
            expected_sim_ids.append(df[1:2].iat[0, sim_count])

            # Validate every single 'Infected' are same in these 2 files
            insetchart_string = s.retrieve_output_files(paths=['output/InsetChart.json'])
            insetchart_dict = json.loads(insetchart_string[0].decode('utf-8'))
            infected_json_from_file = insetchart_dict['Channels']['Infected']['Data']
            actual_infected_data = []
            expected_infected_data = []
            for i in range(0, len(infected_json_from_file)):
                actual_infected_data.append(infected_json_from_file[i])
                expected_infected_data.append(float(df[2:].iloc[i, sim_count]))
            self.assertEqual(actual_infected_data, expected_infected_data)
            sim_count = sim_count + 1

        self.assertSetEqual(set(actual_sim_ids_in_comps), set(expected_sim_ids))

    def test_analyzer_preidmtools_exp(self):
        # delete output from previous run
        del_folder("output")

        # create a new empty 'output' dir
        os.mkdir("output")

        filenames = ['output/InsetChart.json', 'config.json']
        analyzers = [DownloadAnalyzer(filenames=filenames, output_path='output')]

        exp_id = ('f48e09d4-acd9-e911-a2be-f0921c167861', ItemType.EXPERIMENT)  # comps2

        am = AnalyzeManager(platform=self.p, ids=[exp_id], analyzers=analyzers)
        am.analyze()

        for simulation in Experiment.get(exp_id[0]).get_simulations():
            s = simulation.get(id=simulation.id)
            self.assertTrue(os.path.exists(os.path.join('output', str(s.id), "config.json")))
            self.assertTrue(os.path.exists(os.path.join('output', str(s.id), "InsetChart.json")))

    def test_download_analyzer_suite(self):
        # delete output from previous run
        del_folder("output")

        # create a new empty 'output' dir
        os.mkdir("output")

        filenames = ['output/InsetChart.json']
        analyzers = [DownloadAnalyzer(filenames=filenames, output_path='output')]

        suite_id = 'e00296a6-0200-ea11-a2be-f0921c167861'
        suite_list = [(suite_id, ItemType.SUITE)]  # comps2 staging
        am = AnalyzeManager(platform=self.p, ids=suite_list, analyzers=analyzers)
        am.analyze()

        # verify results:
        # retrieve suite from comps
        comps_suite = self.p.get_platform_item(item_id=suite_id, item_type=ItemType.SUITE)
        # retrieve experiment from suite
        exps = self.p.get_children_for_platform_item(comps_suite)
        comps_exp = self.p.get_platform_item(item_id=exps[0].uid, item_type=ItemType.EXPERIMENT)
        sims = self.p.get_children_for_platform_item(comps_exp)
        for simulation in sims:
            self.assertTrue(os.path.exists(os.path.join('output', str(simulation.uid), "InsetChart.json")))
