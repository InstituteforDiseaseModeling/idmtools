import os
import pytest
import json
import shutil
import numpy as np
from functools import partial

from COMPS.Data import Experiment
from idmtools.builders import ExperimentBuilder
from idmtools.managers import ExperimentManager
from idmtools_models.dtk import DTKExperiment
from idmtools_models.dtk.defaults import DTKSIR
from idmtools_platform_comps.COMPSPlatform import COMPSPlatform
from idmtools.core.PlatformFactory import PlatformFactory
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.ITestWithPersistence import ITestWithPersistence
from idmtools.analysis.AnalyzeManager import AnalyzeManager
from idmtools.analysis.AddAnalyzer import AddAnalyzer
from idmtools.analysis.DownloadAnalyzer import DownloadAnalyzer
from analyzers.PopulationAnalyzer import PopulationAnalyzer
from idmtools.utils.file_parser import FileParser
from idmtools_test.utils.utils import del_file, del_folder

current_directory = os.path.dirname(os.path.realpath(__file__))


def param_update(simulation, param, value):
    return simulation.set_parameter(param, value)


setA = partial(param_update, param="a")
setB = partial(param_update, param="b")
setC = partial(param_update, param="c")
setD = partial(param_update, param="d")


class TestAnalyzeManager(ITestWithPersistence):

    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        print(self.case_name)
        self.p = COMPSPlatform()

        e = DTKExperiment.from_default(self.case_name, default=DTKSIR,
                                       eradication_path=os.path.join(COMMON_INPUT_PATH, "dtk", "Eradication.exe"))
        e.tags = {"idmtools": "idmtools-automation", "string_tag": "test", "number_tag": 123}

        e.base_simulation.set_parameter("Enable_Immunity", 0)

        def param_a_update(simulation, value):
            simulation.set_parameter("Run_Number", value)
            return {"Run_Number": value}

        self.builder = ExperimentBuilder()
        # Sweep parameter "Run_Number"
        self.builder.add_sweep_definition(param_a_update, range(0, 2))
        e.builder = self.builder
        em = ExperimentManager(platform=self.p, experiment=e)
        em.run()
        em.wait_till_done()
        self.assertTrue(e.succeeded)
        self.exp_id = em.experiment.uid

        # Uncomment out if you do not want to regenerate exp and sims
        # self.exp_id = '9eacbb9a-5ecf-e911-a2bb-f0921c167866' #comps2 staging

    @pytest.mark.skip("Do not run - this is broken")
    def test_AddAnalyzer(self):

        analyzers = [AddAnalyzer()]
        platform = PlatformFactory.create(key='COMPS')

        am = AnalyzeManager(configuration={}, platform=platform, ids=[self.exp_id], analyzers=analyzers)
        am.analyze()

    def test_DownloadAnalyzer(self):
        #delete output from previous run
        del_folder("output")

        # create a new empty 'output' dir
        os.mkdir("output")

        filenames = ['output\\InsetChart.json', 'config.json']
        analyzers = [DownloadAnalyzer(filenames=filenames, output_path='output')]
        platform = PlatformFactory.create(key='COMPS')

       # exp_id = '9eacbb9a-5ecf-e911-a2bb-f0921c167866'

        am = AnalyzeManager(configuration={}, platform=platform, ids=[self.exp_id], analyzers=analyzers)
        am.analyze()

        for simulation in Experiment.get(self.exp_id).get_simulations():
            s = simulation.get(id=simulation.id)
            self.assertTrue(os.path.exists(os.path.join('output', str(s.id), "config.json")))
            self.assertTrue(os.path.exists(os.path.join('output', str(s.id), "insetChart.json")))

    def test_PopulationAnalyzer(self):
        # del_file(os.path.join(COMMON_INPUT_PATH, 'analyzers', 'population.csv'))
        # del_file(os.path.join(COMMON_INPUT_PATH, 'analyzers', 'population.png'))

        analyzers = [PopulationAnalyzer()]
        platform = PlatformFactory.create(key='COMPS')

        am = AnalyzeManager(configuration={}, platform=platform, ids=self.exp_id, analyzers=analyzers)
        am.analyze()

        # -----------------------------------------------------------------------------------------------------
        # Compare "Statistical Population" values in PopulationAnalyzer's output file: 'population.csv'
        # with COMPS's out\InsetChart.json for each simulation
        # -----------------------------------------------------------------------------------------------------

        df = FileParser.load_csv_file(os.path.join(COMMON_INPUT_PATH, 'analyzers', 'population.csv'))
        sim_count = 1

        for simulation in Experiment.get(self.exp_id).get_simulations():
            s = simulation.get(id=simulation.id)
            print(simulation.id)
            # Validate simulation ids are the same between population.csv and insetchart.json
            self.assertEqual(str(s.id), df[1:2].iat[0, sim_count])

            insetchartFileString = s.retrieve_output_files(paths=['output/InsetChart.json'])
            insetchartDict = json.loads(insetchartFileString[0].decode('utf-8'))
            population_data = insetchartDict['Channels']['Statistical Population']['Data']
            # Validate every single Statistical Population' from insetChart.json are equals to population.csv file
            for i in range(0, len(population_data), 1):
                self.assertEqual(str(population_data[i]), df[2:].iloc[i, sim_count])
            sim_count = sim_count + 1
