import json
import os
import sys
from functools import partial

import pytest
from COMPS.Data import Experiment as COMPSExperiment
from idmtools.analysis.add_analyzer import AddAnalyzer
from idmtools.analysis.analyze_manager import AnalyzeManager
from idmtools.analysis.csv_analyzer import CSVAnalyzer
from idmtools.analysis.download_analyzer import DownloadAnalyzer
from idmtools.analysis.tags_analyzer import TagsAnalyzer
from idmtools.assets import Asset
from idmtools.builders import SimulationBuilder
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools_test.utils.utils import del_file, del_folder, load_csv_file

analyzer_path = os.path.join(os.path.dirname(__file__), "inputs")
sys.path.insert(0, analyzer_path)
from PopulationAnalyzer1 import PopulationAnalyzer # noqa
from TimeseriesAnalyzer import TimeseriesAnalyzer # noqa

DEFAULT_INPUT_PATH = os.path.join(COMMON_INPUT_PATH)
DEFAULT_ERADICATION_PATH = os.path.join(DEFAULT_INPUT_PATH, "emod", "Eradication.exe")
DEFAULT_CONFIG_PATH = os.path.join(DEFAULT_INPUT_PATH, "emod_files", "config.json")
DEFAULT_CAMPAIGN_PATH = os.path.join(DEFAULT_INPUT_PATH, "emod_files", "campaign.json")
DEFAULT_DEMO_PATH = os.path.join(DEFAULT_INPUT_PATH, "emod_files", "demographics.json")


def param_update(simulation, param, value):
    return simulation.set_parameter(param, value)


setA = partial(param_update, param="a")
setB = partial(param_update, param="b")
setC = partial(param_update, param="c")
setD = partial(param_update, param="d")


@pytest.mark.comps
@pytest.mark.analysis
class TestAnalyzeManagerEmodComps(ITestWithPersistence):

    def generate_experiment(self):

        command = "Assets/Eradication.exe --config config.json --input-path ./Assets"
        task = CommandTask(command=command)
        with open(DEFAULT_CONFIG_PATH, 'r') as cin:
            task.config = json.load(cin)
            # task.config["parameters"]["Demographics_Filenames"][0] = "Assets/" + task.config["parameters"]["Demographics_Filenames"][0]
            task.config["parameters"]["Campaign_Filename"] = "Assets/" + task.config["parameters"]["Campaign_Filename"]

        def save_config(task):
            return Asset(filename='config.json', content=json.dumps(task.config))
        # task.gather_transient_asset_hooks.append(save_config)
        task.transient_assets.add_asset(save_config(task))

        def update_param(simulation, param, value):
            simulation.task.config[param] = value
            return{param: value}

        set_run_number = partial(update_param, param="Run_Number")

        # add eradication.exe to current dir in comps
        eradication_asset = Asset(absolute_path=DEFAULT_ERADICATION_PATH)
        task.common_assets.add_asset(eradication_asset)

        # add config.json/campaign/demographic.json to current dir in comps
        campaign_asset = Asset(absolute_path=DEFAULT_CAMPAIGN_PATH)
        demo_asset = Asset(absolute_path=DEFAULT_DEMO_PATH)

        task.common_assets.add_asset(campaign_asset)
        task.common_assets.add_asset(demo_asset)

        builder = SimulationBuilder()
        builder.add_sweep_definition(set_run_number, range(0, 2))
        # create experiment from task
        experiment = Experiment.from_builder(builder, task, name="test_analyzers_emod_comps.py")

        self.platform.run_items(experiment)
        self.platform.wait_till_done(experiment)
        self.exp_id = experiment.uid

    @classmethod
    def setUpClass(cls):
        cls.platform = Platform('COMPS2')
        cls.generate_experiment(cls)

    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        print(self.case_name)

    @pytest.mark.long
    def test_AddAnalyzer(self):
        filenames = ['StdOut.txt']
        analyzers = [AddAnalyzer(filenames=filenames)]
        # self.generate_experiment()
        am = AnalyzeManager(platform=self.platform, ids=[(self.exp_id, ItemType.EXPERIMENT)], analyzers=analyzers)
        am.analyze()

    @pytest.mark.long
    def test_DownloadAnalyzer(self):
        # delete output from previous run
        del_folder("output")

        # create a new empty 'output' dir
        os.mkdir("output")

        # self.generate_experiment()

        filenames = ['output/InsetChart.json', 'config.json']
        analyzers = [DownloadAnalyzer(filenames=filenames, output_path='output')]

        am = AnalyzeManager(platform=self.platform, ids=[(self.exp_id, ItemType.EXPERIMENT)], analyzers=analyzers)
        am.analyze()

        for simulation in COMPSExperiment.get(self.exp_id).get_simulations():
            self.assert_sim_has_config_and_inset_chart(simulation)

    def assert_sim_has_config_and_inset_chart(self, simulation):
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
        am = AnalyzeManager(platform=self.platform, ids=exp_list, analyzers=analyzers)
        am.analyze()

    @pytest.mark.long
    def test_population_analyzer(self):
        del_file(os.path.join(analyzer_path, 'population.csv'))
        del_file(os.path.join(analyzer_path, 'population.png'))
        # self.generate_experiment()

        # self.exp_id = uuid.UUID("fc59240c-07db-e911-a2be-f0921c167861")
        filenames = ['output/InsetChart.json']

        analyzers = [PopulationAnalyzer(filenames)]

        am = AnalyzeManager(platform=self.platform, ids=[(self.exp_id, ItemType.EXPERIMENT)], analyzers=analyzers)
        am.analyze()

        # -----------------------------------------------------------------------------------------------------
        # Compare "Statistical Population" values in PopulationAnalyzer's output file: 'population.csv'
        # with COMPS's out\InsetChart.json for each simulation
        # -----------------------------------------------------------------------------------------------------
        df = load_csv_file(os.path.join(analyzer_path, 'population.csv'))
        sim_count = 1
        expected_sim_ids = []
        actual_sim_ids_in_comps = []
        for simulation in COMPSExperiment.get(self.exp_id).get_simulations():
            insetchart_dict = self.assert_has_inset(actual_sim_ids_in_comps, df, expected_sim_ids, sim_count,
                                                    simulation)
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
        del_file(os.path.join(analyzer_path, 'timeseries.csv'))
        del_file(os.path.join(analyzer_path, 'timeseries.png'))

        # self.generate_experiment()

        filenames = ['output/InsetChart.json']
        analyzers = [TimeseriesAnalyzer(filenames=filenames)]

        # self.exp_id = uuid.UUID("fc59240c-07db-e911-a2be-f0921c167861")
        am = AnalyzeManager(platform=self.platform, ids=[(self.exp_id, ItemType.EXPERIMENT)], analyzers=analyzers)
        am.analyze()

        # ------------------------------------------------------------------------------
        # Step3: Compare 'Adult Vector' channel in timeserier.csv and COMPS's out\InsetChart.json's 'Adult Vector'
        # ------------------------------------------------------------------------------
        df = load_csv_file(os.path.join(analyzer_path, 'timeseries.csv'))
        sim_count = 1
        expected_sim_ids = []
        actual_sim_ids_in_comps = []
        for simulation in COMPSExperiment.get(self.exp_id).get_simulations():
            insetchart_dict = self.assert_has_inset(actual_sim_ids_in_comps, df, expected_sim_ids, sim_count,
                                                    simulation)
            infected_json_from_file = insetchart_dict['Channels']['Infected']['Data']
            actual_infected_data = []
            expected_infected_data = []
            for i in range(0, len(infected_json_from_file)):
                actual_infected_data.append(infected_json_from_file[i])
                expected_infected_data.append(float(df[2:].iloc[i, sim_count]))
            self.assertEqual(actual_infected_data, expected_infected_data)
            sim_count = sim_count + 1

        self.assertSetEqual(set(actual_sim_ids_in_comps), set(expected_sim_ids))

    def assert_has_inset(self, actual_sim_ids_in_comps, df, expected_sim_ids, sim_count, simulation):
        s = simulation.get(id=simulation.id)
        actual_sim_ids_in_comps.append(str(s.id))
        expected_sim_ids.append(df[1:2].iat[0, sim_count])
        # Validate every single 'Infected' are same in these 2 files
        insetchart_string = s.retrieve_output_files(paths=['output/InsetChart.json'])
        insetchart_dict = json.loads(insetchart_string[0].decode('utf-8'))
        return insetchart_dict

    def test_analyzer_preidmtools_exp(self):
        # delete output from previous run
        del_folder("output")

        # create a new empty 'output' dir
        os.mkdir("output")

        filenames = ['output/InsetChart.json', 'config.json']
        analyzers = [DownloadAnalyzer(filenames=filenames, output_path='output')]

        exp_id = ('f48e09d4-acd9-e911-a2be-f0921c167861', ItemType.EXPERIMENT)  # comps2

        am = AnalyzeManager(platform=self.platform, ids=[exp_id], analyzers=analyzers)
        am.analyze()

        for simulation in COMPSExperiment.get(exp_id[0]).get_simulations():
            self.assert_sim_has_config_and_inset_chart(simulation)

    def test_download_analyzer_suite(self):
        # delete output from previous run
        del_folder("output")

        # create a new empty 'output' dir
        os.mkdir("output")

        filenames = ['output/InsetChart.json']
        analyzers = [DownloadAnalyzer(filenames=filenames, output_path='output')]

        suite_id = 'e00296a6-0200-ea11-a2be-f0921c167861'
        suite_list = [(suite_id, ItemType.SUITE)]  # comps2 staging
        am = AnalyzeManager(platform=self.platform, ids=suite_list, analyzers=analyzers)
        am.analyze()

        # verify results:
        # retrieve suite from comps
        comps_suite = self.platform.get_item(item_id=suite_id, item_type=ItemType.SUITE)
        # retrieve experiment from suite
        exps = self.platform.get_children_by_object(comps_suite)
        comps_exp = self.platform.get_item(item_id=exps[0].uid, item_type=ItemType.EXPERIMENT)
        sims = self.platform.get_children_by_object(comps_exp)
        for simulation in sims:
            self.assertTrue(os.path.exists(os.path.join('output', str(simulation.uid), "InsetChart.json")))

    @pytest.mark.long
    def test_tags_analyzer_emod_exp(self):
        experiment_id = '36d8bfdc-83f6-e911-a2be-f0921c167861'  # staging exp id JSuresh's Magude exp

        # delete output from previous run
        output_dir = "output_tag"
        del_folder(output_dir)
        analyzers = [TagsAnalyzer()]

        manager = AnalyzeManager(platform=self.platform, partial_analyze_ok=True,
                                 ids=[(experiment_id, ItemType.EXPERIMENT)],
                                 analyzers=analyzers)
        manager.analyze()

        # verify results
        self.assertTrue(os.path.exists(os.path.join(output_dir, "tags.csv")))

    def test_csv_analyzer_emod_exp(self):
        experiment_id = '9311af40-1337-ea11-a2be-f0921c167861'  # staging exp id with csv from config
        # delete output from previous run
        output_dir = "output_csv"
        del_folder(output_dir)
        filenames = ['output/c.csv']
        analyzers = [CSVAnalyzer(filenames=filenames)]

        manager = AnalyzeManager(platform=self.platform, partial_analyze_ok=True,
                                 ids=[(experiment_id, ItemType.EXPERIMENT)],
                                 analyzers=analyzers)
        manager.analyze()

        # verify results
        self.assertTrue(os.path.exists(os.path.join(output_dir, "CSVAnalyzer.csv")))

    def test_csv_analyzer_emod_exp_non_csv_error(self):
        experiment_id = '36d8bfdc-83f6-e911-a2be-f0921c167861'  # staging exp id JSuresh's Magude exp

        # delete output from previous run
        output_dir = "output_csv"
        del_folder(output_dir)
        filenames = ['output/MalariaPatientReport.json']
        with self.assertRaises(Exception) as context:
            analyzers = [CSVAnalyzer(filenames=filenames)]
            manager = AnalyzeManager(platform=self.platform, partial_analyze_ok=True,
                                     ids=[(experiment_id, ItemType.EXPERIMENT)],
                                     analyzers=analyzers)
            manager.analyze()

        self.assertIn('Please ensure all filenames provided to CSVAnalyzer have a csv extension.',
                      context.exception.args[0])

    def test_multi_csv_analyzer_emod_exp(self):
        experiment_id = '1bddce22-0c37-ea11-a2be-f0921c167861'  # staging exp id PythonExperiment with 2 csv outputs

        # delete output from previous run
        output_dir = "output_csv"
        del_folder(output_dir)

        filenames = ['output/a.csv', 'output/b.csv']
        analyzers = [CSVAnalyzer(filenames=filenames)]

        manager = AnalyzeManager(platform=self.platform, partial_analyze_ok=True,
                                 ids=[(experiment_id, ItemType.EXPERIMENT)],
                                 analyzers=analyzers)
        manager.analyze()

        # verify results
        self.assertTrue(os.path.exists(os.path.join(output_dir, "CSVAnalyzer.csv")))
