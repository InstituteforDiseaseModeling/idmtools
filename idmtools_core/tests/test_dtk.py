import json
import os

from COMPS.Data import Experiment
from idmtools.builders import ExperimentBuilder, StandAloneSimulationsBuilder
from idmtools.managers import ExperimentManager
from idmtools.platforms import COMPSPlatform
from tests.utils.decorators import comps_test
from tests.utils.ITestWithPersistence import ITestWithPersistence
from idmtools_models.dtk import DTKExperiment
from idmtools_models.dtk.defaults import DTKSIR

current_directory = os.path.dirname(os.path.realpath(__file__))
INPUT_PATH = os.path.join(current_directory, "inputs")


@comps_test
class TestDTK(ITestWithPersistence):

    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        print(self.case_name)
        self.p = COMPSPlatform(endpoint="https://comps2.idmod.org", environment="Bayesian")

    def test_sir_with_StandAloneSimulationsBuilder(self):
        e = DTKExperiment.from_default(self.case_name, default=DTKSIR,
                                       eradication_path=os.path.join(INPUT_PATH, "dtk", "Eradication.exe"))
        e.tags = {"idmtools": "idmtools-automation", "string_tag": "test", "number_tag": 123}
        #sim = e.simulation() #issue 138
        sim = e.base_simulation
        sim.set_parameter("Enable_Immunity", 0)
        b = StandAloneSimulationsBuilder()
        b.add_simulation(sim)
        e.builder = b

        em = ExperimentManager(platform=self.p, experiment=e)
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
                                       eradication_path=os.path.join(INPUT_PATH, "dtk", "Eradication.exe"))
        e.tags = {"idmtools": "idmtools-automation", "string_tag": "test", "number_tag": 123}

        e.base_simulation.set_parameter("Enable_Immunity", 0)

        def param_a_update(simulation, value):
            simulation.set_parameter("Run_Number", value)
            return {"Run_Number": value}

        builder = ExperimentBuilder()
        # Sweep parameter "Run_Number"
        builder.add_sweep_definition(param_a_update, range(0, 2))
        e.builder = builder
        em = ExperimentManager(platform=self.p, experiment=e)
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

    def test_batch_simulations(self):
        e = DTKExperiment.from_default(self.case_name, default=DTKSIR,
                                       eradication_path=os.path.join(INPUT_PATH, "dtk", "Eradication.exe"))
        e.tags = {"idmtools": "idmtools-automation", "string_tag": "test", "number_tag": 123}
        b = StandAloneSimulationsBuilder()
        #sim = e.simulation() #issue 138
        for i in range(20):
            sim = e.base_simulation
            sim.set_parameter("Enable_Immunity", 0)
            b.add_simulation(sim)

        e.builder = b

        em = ExperimentManager(platform=self.p, experiment=e)
        em.run()
        em.wait_till_done()
        self.assertTrue(e.succeeded)
        exp_id = em.experiment.uid
        for simulation in Experiment.get(exp_id).get_simulations():
            config_string = simulation.retrieve_output_files(paths=["config.json"])
            config_parameters = json.loads(config_string[0].decode('utf-8'))["parameters"]
            self.assertEqual(config_parameters["Enable_Immunity"], 0)

    def test_batch_simulations1(self):
        e = DTKExperiment.from_default(self.case_name, default=DTKSIR,
                                       eradication_path=os.path.join(INPUT_PATH, "dtk", "Eradication.exe"))
        e.tags = {"idmtools": "idmtools-automation", "string_tag": "test", "number_tag": 123}

        e.base_simulation.set_parameter("Enable_Immunity", 0)

        def param_a_update(simulation, value):
            simulation.set_parameter("Run_Number", value)
            return {"Run_Number": value}

        builder = ExperimentBuilder()
        # Sweep parameter "Run_Number"
        builder.add_sweep_definition(param_a_update, range(0, 20))
        e.builder = builder
        em = ExperimentManager(platform=self.p, experiment=e)
        em.run()
        em.wait_till_done()
        self.assertTrue(e.succeeded)
