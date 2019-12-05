import json
import os
import unittest

import pytest

from COMPS.Data import Experiment

from idmtools.core.platform_factory import Platform
from idmtools.builders import StandAloneSimulationsBuilder
from idmtools.managers import ExperimentManager
from idmtools_model_emod import EMODExperiment

from idmtools_test import COMMON_INPUT_PATH
from idmtools.assets import AssetCollection
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence


@pytest.mark.comps
class TestExperiments(ITestWithPersistence):

    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        print(self.case_name)
        self.platform = Platform("COMPS")

    @unittest.skipIf(not os.getenv('WAIT_FOR_BUG_FIX', '0') == '1', reason="eradication load 2 times")
    def test_emod_experiment_endpointsanalyzer_example(self):
        DEFAULT_CONFIG_PATH = os.path.join(COMMON_INPUT_PATH, "custom", "config.json")
        DEFAULT_CAMPAIGN_JSON = os.path.join(COMMON_INPUT_PATH, "custom", "campaign.json")
        DEFAULT_DEMOGRAPHICS_JSON = os.path.join(COMMON_INPUT_PATH, "custom", "demo.json")
        DEFAULT_ERADICATION_PATH = os.path.join(COMMON_INPUT_PATH, "custom", "Eradication.exe")

        experiment = EMODExperiment.from_files(self.case_name,
                                               eradication_path=DEFAULT_ERADICATION_PATH,
                                               config_path=DEFAULT_CONFIG_PATH,
                                               campaign_path=DEFAULT_CAMPAIGN_JSON,
                                               demographics_paths=DEFAULT_DEMOGRAPHICS_JSON)
        experiment.tags = {"idmtools": "idmtools-automation", "catch": "sianyoola", "rcd": "false"}
        experiment.name = 'malaria_sianyoola_interventions'

        # additional emod custom assets including custom_reports, climate files, migration files
        asset_collection = AssetCollection()
        asset_collection.add_directory(assets_directory=os.path.join(COMMON_INPUT_PATH, "custom"))
        experiment.add_assets(asset_collection)

        builder = StandAloneSimulationsBuilder()
        for i in range(2):
            simulation = experiment.simulation()
            simulation.set_parameter("Enable_Immunity", 0)
            builder.add_simulation(simulation)
        experiment.builder = builder

        em = ExperimentManager(experiment=experiment, platform=self.platform)
        em.run()
        em.wait_till_done()
        self.assertTrue(experiment.succeeded)
        exp_id = em.experiment.uid
        for simulation in Experiment.get(exp_id).get_simulations():
            config_string = simulation.retrieve_output_files(paths=["config.json"])
            config_parameters = json.loads(config_string[0].decode('utf-8'))["parameters"]
            self.assertEqual(config_parameters["Enable_Immunity"], 0)
