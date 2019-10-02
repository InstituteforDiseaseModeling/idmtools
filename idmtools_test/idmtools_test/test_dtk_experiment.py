import json
import os
import pytest

from COMPS.Data import Experiment

from idmtools.builders import ExperimentBuilder, StandAloneSimulationsBuilder
from idmtools.managers import ExperimentManager
from idmtools_model_dtk import DTKExperiment
from idmtools_platform_comps.COMPSPlatform import COMPSPlatform
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.ITestWithPersistence import ITestWithPersistence
from idmtools.assets import AssetCollection, Asset


@pytest.mark.comps
class TestExperiments(ITestWithPersistence):

    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        print(self.case_name)
        self.p = COMPSPlatform()

    def test_dtk_experiment_endpointsanalyzer_example(self):
        DEFAULT_CONFIG_PATH = os.path.join(COMMON_INPUT_PATH, "custom", "config.json")
        DEFAULT_CAMPAIGN_JSON = os.path.join(COMMON_INPUT_PATH, "custom", "campaign.json")
        DEFAULT_DEMOGRAPHICS_JSON = os.path.join(COMMON_INPUT_PATH, "custom", "demo.json")
        DEFAULT_ERADICATION_PATH = os.path.join(COMMON_INPUT_PATH, "custom", "Eradication.exe")

        e = DTKExperiment.from_files(self.case_name,
                                     eradication_path=DEFAULT_ERADICATION_PATH,
                                     config_path=DEFAULT_CONFIG_PATH,
                                     campaign_path=DEFAULT_CAMPAIGN_JSON,
                                     demographics_paths=DEFAULT_DEMOGRAPHICS_JSON
                                     )
        e.tags = {"idmtools": "idmtools-automation", "catch": "sianyoola", "rcd": "false"}
        e.name = 'malaria_sianyoola_interventions'

        # additional dtk custom assets including custom_reports, climate files, migration files
        ac = AssetCollection()
        ac.add_directory(assets_directory=os.path.join(COMMON_INPUT_PATH, "custom"))

        e.add_assets(ac)

        b = StandAloneSimulationsBuilder()

        for i in range(2):
            sim = e.simulation()
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
