import json
import os

import pytest
from COMPS.Data import Experiment

from idmtools.builders import ExperimentBuilder, StandAloneSimulationsBuilder
from idmtools.core.platform_factory import PlatformFactory
from idmtools.managers import ExperimentManager
from idmtools_model_dtk import DTKExperiment
from idmtools_model_dtk.defaults import DTKSIR
from idmtools_platform_comps.comps_platform import COMPSPlatform
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence

current_directory = os.path.dirname(os.path.realpath(__file__))
DEFAULT_CONFIG_PATH = os.path.join(COMMON_INPUT_PATH, "files", "config.json")
DEFAULT_CAMPAIGN_JSON = os.path.join(COMMON_INPUT_PATH, "files", "campaign.json")
DEFAULT_DEMOGRAPHICS_JSON = os.path.join(COMMON_INPUT_PATH, "files", "demographics.json")
DEFAULT_ERADICATION_PATH = os.path.join(COMMON_INPUT_PATH, "dtk", "Eradication.exe")


@pytest.mark.comps
class TestDTK(ITestWithPersistence):

    @classmethod
    def setUpClass(cls):
        cls.platform = PlatformFactory.create_from_block('COMPS')

    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        print(self.case_name)

    def test_sir_with_StandAloneSimulationsBuilder(self):
        e = DTKExperiment.from_default(self.case_name, default=DTKSIR,
                                       eradication_path=os.path.join(COMMON_INPUT_PATH, "dtk", "Eradication.exe"))
        e.tags = {"idmtools": "idmtools-automation", "string_tag": "test", "number_tag": 123}
        sim = e.simulation()
        sim.set_parameter("Enable_Immunity", 0)
        b = StandAloneSimulationsBuilder()
        b.add_simulation(sim)
        e.builder = b

        em = ExperimentManager(platform=self.platform, experiment=e)
        em.run()
        em.wait_till_done()
        self.assertTrue(e.succeeded)
        exp_id = em.experiment.uid
        for simulation in Experiment.get(exp_id).get_simulations():
            configString = simulation.retrieve_output_files(paths=["config.json"])
            config_parameters = json.loads(configString[0].decode('utf-8'))["parameters"]
            self.assertEqual(config_parameters["Enable_Immunity"], 0)

    def test_sir_with_ExperimentBuilder(self):
        e = DTKExperiment.from_default(self.case_name, default=DTKSIR,
                                       eradication_path=os.path.join(COMMON_INPUT_PATH, "dtk", "Eradication.exe"))
        e.tags = {"idmtools": "idmtools-automation", "string_tag": "test", "number_tag": 123}

        e.base_simulation.set_parameter("Enable_Immunity", 0)

        def param_a_update(simulation, value):
            simulation.set_parameter("Run_Number", value)
            return {"Run_Number": value}

        builder = ExperimentBuilder()
        # Sweep parameter "Run_Number"
        builder.add_sweep_definition(param_a_update, range(0, 2))
        e.builder = builder
        em = ExperimentManager(platform=self.platform, experiment=e)
        em.run()
        em.wait_till_done()
        self.assertTrue(e.succeeded)
        exp_id = em.experiment.uid
        run_number = 0
        for simulation in Experiment.get(exp_id).get_simulations():
            configString = simulation.retrieve_output_files(paths=["config.json"])
            config_parameters = json.loads(configString[0].decode('utf-8'))["parameters"]
            self.assertEqual(config_parameters["Enable_Immunity"], 0)
            self.assertEqual(config_parameters["Run_Number"], run_number)
            run_number = run_number + 1

    def test_batch_simulations_StandAloneSimulationsBuilder(self):
        e = DTKExperiment.from_default(self.case_name, default=DTKSIR,
                                       eradication_path=os.path.join(COMMON_INPUT_PATH, "dtk", "Eradication.exe"))
        e.tags = {"idmtools": "idmtools-automation", "string_tag": "test", "number_tag": 123}
        b = StandAloneSimulationsBuilder()

        for i in range(20):
            sim = e.simulation()
            sim.set_parameter("Enable_Immunity", 0)
            b.add_simulation(sim)

        e.builder = b

        em = ExperimentManager(platform=self.platform, experiment=e)
        em.run()
        em.wait_till_done()
        self.assertTrue(e.succeeded)
        exp_id = em.experiment.uid
        for simulation in Experiment.get(exp_id).get_simulations():
            config_string = simulation.retrieve_output_files(paths=["config.json"])
            config_parameters = json.loads(config_string[0].decode('utf-8'))["parameters"]
            self.assertEqual(config_parameters["Enable_Immunity"], 0)

    def test_batch_simulations_ExperimentBuilder(self):

        e = DTKExperiment.from_default(self.case_name, default=DTKSIR,
                                       eradication_path=os.path.join(COMMON_INPUT_PATH, "dtk", "Eradication.exe"))
        e.tags = {"idmtools": "idmtools-automation", "string_tag": "test", "number_tag": 123}
        # s = Suite(name="test suite")
        # s.experiments.append(e)
        e.base_simulation.set_parameter("Enable_Immunity", 0)

        def param_a_update(simulation, value):
            simulation.set_parameter("Run_Number", value)
            return {"Run_Number": value}

        builder = ExperimentBuilder()
        # Sweep parameter "Run_Number"
        builder.add_sweep_definition(param_a_update, range(0, 20))
        e.builder = builder
        em = ExperimentManager(platform=self.platform, experiment=e)
        em.run()
        em.wait_till_done()
        self.assertTrue(e.succeeded)

    def test_load_files(self):
        e = DTKExperiment.from_files(self.case_name,
                                     eradication_path=DEFAULT_ERADICATION_PATH,
                                     config_path=DEFAULT_CONFIG_PATH,
                                     campaign_path=DEFAULT_CAMPAIGN_JSON,
                                     demographics_paths=DEFAULT_DEMOGRAPHICS_JSON
                                     )

        e.tags = {"idmtools": "idmtools-automation", "string_tag": "test", "number_tag": 123}
        sim = e.simulation()
        sim.set_parameter("Enable_Immunity", 0)
        b = StandAloneSimulationsBuilder()
        b.add_simulation(sim)
        e.builder = b

        em = ExperimentManager(platform=self.platform, experiment=e)
        em.run()
        em.wait_till_done()
        self.assertTrue(e.succeeded)

        exp_id = em.experiment.uid
        for simulation in Experiment.get(exp_id).get_simulations():
            configString = simulation.retrieve_output_files(paths=["config.json"])
            config_parameters = json.loads(configString[0].decode('utf-8'))["parameters"]
            self.assertEqual(config_parameters["Enable_Immunity"], 0)

    def test_load_files_2(self):

        e = DTKExperiment.from_default(self.case_name, default=DTKSIR,
                                       eradication_path=DEFAULT_ERADICATION_PATH)

        e.base_simulation.load_files(demographics_paths=DEFAULT_DEMOGRAPHICS_JSON)

        e.tags = {"idmtools": "idmtools-automation", "string_tag": "test", "number_tag": 123}
        sim = e.simulation()
        sim.set_parameter("Enable_Immunity", 0)
        b = StandAloneSimulationsBuilder()
        b.add_simulation(sim)
        e.builder = b

        em = ExperimentManager(platform=self.platform, experiment=e)
        em.run()
        em.wait_till_done()
        self.assertTrue(e.succeeded)

        exp_id = em.experiment.uid
        for simulation in Experiment.get(exp_id).get_simulations():
            configString = simulation.retrieve_output_files(paths=["config.json"])
            config_parameters = json.loads(configString[0].decode('utf-8'))["parameters"]
            self.assertEqual(config_parameters["Enable_Immunity"], 0)
