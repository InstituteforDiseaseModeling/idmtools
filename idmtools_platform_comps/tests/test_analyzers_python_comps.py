import os
import unittest

from functools import partial

from COMPS.Data import Experiment
from idmtools.builders import ExperimentBuilder
from idmtools.core.platform_factory import Platform
from idmtools.managers import ExperimentManager
from idmtools.core import EntityStatus
from idmtools_models.python import PythonExperiment
from idmtools_test import COMMON_INPUT_PATH
from idmtools.analysis.AnalyzeManager import AnalyzeManager
from idmtools.analysis.DownloadAnalyzer import DownloadAnalyzer
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools_test.utils.utils import del_folder

current_directory = os.path.dirname(os.path.realpath(__file__))


def param_update(simulation, param, value):
    return simulation.set_parameter(param, value)


setA = partial(param_update, param="a")
setB = partial(param_update, param="b")
setC = partial(param_update, param="c")
setD = partial(param_update, param="d")


class TestAnalyzeManagerPythonComps(ITestWithPersistence):


    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        print(self.case_name)
        self.p = Platform('COMPS2')

    def create_experiment(self):
        pe = PythonExperiment(name=self.case_name, model_path=os.path.join(COMMON_INPUT_PATH, "python", "model1.py"))
        pe.tags = {"idmtools": "idmtools-automation", "string_tag": "test", "number_tag": 123}

        pe.base_simulation.set_parameter("c", "c-value")

        def param_update_ab(simulation, param, value):
            # Set B within
            if param == "a":
                simulation.set_parameter("b", value + 2)

            return simulation.set_parameter(param, value)

        setAB = partial(param_update_ab, param="a")

        builder = ExperimentBuilder()
        # Sweep parameter "a" and make "b" depends on "a"
        builder.add_sweep_definition(setAB, range(0, 2))
        pe.builder = builder
        em = ExperimentManager(experiment=pe, platform=self.p)
        em.run()
        em.wait_till_done()
        self.assertTrue(all([s.status == EntityStatus.SUCCEEDED for s in pe.children()]))
        experiment = Experiment.get(em.experiment.uid)
        print(experiment.id)
        self.exp_id = experiment.id  # COMPS Experiment object, so .id

        # Uncomment out if you do not want to regenerate exp and sims
        # self.exp_id = '9eacbb9a-5ecf-e911-a2bb-f0921c167866' #comps2 staging

    def test_DownloadAnalyzer(self):
        #delete output from previous run
        del_folder("output")

        # create a new empty 'output' dir
        os.mkdir("output")
        self.create_experiment()
        filenames = ['output\\result.json', 'config.json']
        analyzers = [DownloadAnalyzer(filenames=filenames, output_path='output')]

        am = AnalyzeManager(platform=self.p, ids=[self.exp_id], analyzers=analyzers)
        am.analyze()

        for simulation in Experiment.get(self.exp_id).get_simulations():
            s = simulation.get(id=simulation.id)
            self.assertTrue(os.path.exists(os.path.join('output', str(s.id), "config.json")))
            self.assertTrue(os.path.exists(os.path.join('output', str(s.id), "result.json")))

    def test_analyzer_multiple_experiments(self):
        #delete output from previous run
        del_folder("output")

        # create a new empty 'output' dir
        os.mkdir("output")

        filenames = ['output/result.json', 'config.json']
        analyzers = [DownloadAnalyzer(filenames=filenames, output_path='output')]

        exp_list = ['3ca4491a-0edb-e911-a2be-f0921c167861', '4dcd7149-4eda-e911-a2be-f0921c167861']

        am = AnalyzeManager(platform=self.p, ids=exp_list, analyzers=analyzers)
        am.analyze()
        for exp_id in exp_list:
            for simulation in Experiment.get(exp_id).get_simulations():
                s = simulation.get(id=simulation.id)
                self.assertTrue(os.path.exists(os.path.join('output', str(s.id), "config.json")))
                self.assertTrue(os.path.exists(os.path.join('output', str(s.id), "result.json")))

