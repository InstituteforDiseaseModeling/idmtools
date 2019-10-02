import os
import pytest
import json

from COMPS.Data import Experiment
from idmtools.builders import ExperimentBuilder
from idmtools.managers import ExperimentManager
from idmtools_models.python import PythonExperiment
from idmtools.core import EntityStatus
from idmtools.core.PlatformFactory import PlatformFactory
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.ITestWithPersistence import ITestWithPersistence
from idmtools.analysis.AnalyzeManager import AnalyzeManager
from idmtools.analysis.AddAnalyzer import AddAnalyzer
from idmtools.analysis.DownloadAnalyzer import DownloadAnalyzer
from idmtools.utils.file_parser import FileParser
from idmtools_test.utils.utils import del_folder

from importlib import reload
from idmtools_platform_local.docker.DockerOperations import DockerOperations
from operator import itemgetter
from idmtools_test.utils.confg_local_runner_test import reset_local_broker, get_test_local_env_overrides
from idmtools_test.utils.decorators import restart_local_platform

current_directory = os.path.dirname(os.path.realpath(__file__))


class TestAnalyzeManager(ITestWithPersistence):

    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        print(self.case_name)
        reset_local_broker()
        from idmtools_platform_local.workers.brokers import setup_broker
        setup_broker()
        # ensure we start from no environment
        dm = DockerOperations()
        dm.cleanup(True)

        import idmtools_platform_local.tasks.create_experiment
        import idmtools_platform_local.tasks.create_simulation
        reload(idmtools_platform_local.tasks.create_experiment)
        reload(idmtools_platform_local.tasks.create_simulation)

        platform = PlatformFactory.create_from_block('Local_Staging')

        # CreateSimulationTask.broker =

        name = self.case_name
        pe = PythonExperiment(name=self.case_name, model_path=os.path.join(COMMON_INPUT_PATH, "python", "model1.py"))

        pe.tags = {"idmtools": "idmtools-automation", "string_tag": "test", "number_tag": 123}

        def param_a_update(simulation, value):
            simulation.set_parameter("a", value)
            return {"a": value}

        builder = ExperimentBuilder()
        # Sweep parameter "a"
        builder.add_sweep_definition(param_a_update, range(0, 5))
        pe.builder = builder

        em = ExperimentManager(experiment=pe, platform=platform)
        em.run()
        em.wait_till_done()
        self.assertTrue(all([s.status == EntityStatus.FAILED for s in pe.simulations]))
        # validation
        self.assertEqual(pe.name, name)
        self.assertEqual(pe.simulation_count, 5)
        self.assertIsNotNone(pe.uid)
        self.assertTrue(all([s.status == EntityStatus.FAILED for s in pe.simulations]))
        self.assertFalse(pe.succeeded)

        # validate tags
        tags = []
        for simulation in pe.simulations:
            self.assertEqual(simulation.experiment.uid, pe.uid)
            tags.append(simulation.tags)
        expected_tags = [{'a': 0}, {'a': 1}, {'a': 2}, {'a': 3}, {'a': 4}]
        sorted_tags = sorted(tags, key=itemgetter('a'))
        sorted_expected_tags = sorted(expected_tags, key=itemgetter('a'))
        self.assertEqual(sorted_tags, sorted_expected_tags)
        self.exp_id = pe.uid

        # Uncomment out if you do not want to regenerate exp and sims
        # self.exp_id = '9eacbb9a-5ecf-e911-a2bb-f0921c167866' #comps2 staging

    def test_AddAnalyzer(self):

        analyzers = [AddAnalyzer()]
        platform = PlatformFactory.create(key='Local')

        am = AnalyzeManager(configuration={}, platform=platform, ids=[self.exp_id], analyzers=analyzers)
        am.analyze()

