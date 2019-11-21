import json
import os
import pytest

from idmtools_model_emod import EMODExperiment
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence

current_directory = os.path.dirname(os.path.realpath(__file__))
DEFAULT_CONFIG_PATH = os.path.join(COMMON_INPUT_PATH, "files", "config.json")
DEFAULT_CAMPAIGN_JSON = os.path.join(COMMON_INPUT_PATH, "files", "campaign.json")
DEFAULT_DEMOGRAPHICS_JSON = os.path.join(COMMON_INPUT_PATH, "files", "demographics.json")
DEFAULT_ERADICATION_PATH = os.path.join(COMMON_INPUT_PATH, "emod", "Eradication.exe")


@pytest.mark.comps
@pytest.mark.emod
class TestEMODExperiment(ITestWithPersistence):

    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        print(self.case_name)

    def test_command(self):
        models_dir = os.path.join(COMMON_INPUT_PATH, "fakemodels", "Eradication.exe")
        exp = EMODExperiment(eradication_path=models_dir)
        exp.pre_creation()
        self.assertEqual("Assets/Eradication.exe --config config.json --input-path ./Assets\;. --dll-path ./Assets", exp.command.cmd)

        models_dir = os.path.join(COMMON_INPUT_PATH, "fakemodels", "Eradication")
        exp = EMODExperiment(eradication_path=models_dir)
        exp.pre_creation()
        self.assertEqual("Assets/Eradication --config config.json --input-path ./Assets\;. --dll-path ./Assets", exp.command.cmd)

        models_dir = os.path.join(COMMON_INPUT_PATH, "fakemodels", "Eradication-2.11.custom.exe")
        exp = EMODExperiment(eradication_path=models_dir)
        exp.pre_creation()
        self.assertEqual("Assets/Eradication-2.11.custom.exe --config config.json --input-path ./Assets\;. --dll-path ./Assets",
                         exp.command.cmd)

        models_dir = os.path.join(COMMON_INPUT_PATH, "fakemodels", "AnotherOne")
        exp = EMODExperiment(eradication_path=models_dir)
        exp.pre_creation()
        self.assertEqual("Assets/AnotherOne --config config.json --input-path ./Assets\;. --dll-path ./Assets", exp.command.cmd)

    def test_legacy_emod(self):
        models_dir = os.path.join(COMMON_INPUT_PATH, "fakemodels", "Eradication.exe")
        exp = EMODExperiment(eradication_path=models_dir)
        exp.pre_creation()
        self.assertEqual(f"Assets/Eradication.exe --config config.json --input-path ./Assets\;. --dll-path ./Assets", exp.command.cmd)

        models_dir = os.path.join(COMMON_INPUT_PATH, "fakemodels", "Eradication.exe")
        exp = EMODExperiment(eradication_path=models_dir, legacy_exe=True)
        exp.pre_creation()
        self.assertEqual(f"Assets/Eradication.exe --config config.json --input-path ./Assets --dll-path ./Assets", exp.command.cmd)

    def test_load_files(self):
        e = EMODExperiment.from_files(self.case_name,
                                      eradication_path=DEFAULT_ERADICATION_PATH,
                                      config_path=DEFAULT_CONFIG_PATH,
                                      campaign_path=DEFAULT_CAMPAIGN_JSON,
                                      demographics_paths=DEFAULT_DEMOGRAPHICS_JSON
                                      )

        sim = e.simulation()

        e.pre_creation()

        # Open all the files for comparison
        with open(DEFAULT_CONFIG_PATH, 'r') as fp:
            config = json.load(fp)["parameters"]
        with open(DEFAULT_CAMPAIGN_JSON, 'r') as fp:
            campaign = json.load(fp)
        with open(DEFAULT_DEMOGRAPHICS_JSON, 'r') as fp:
            demog = json.load(fp)

        self.assertEqual(e.eradication_path, DEFAULT_ERADICATION_PATH)
        self.assertIn(DEFAULT_ERADICATION_PATH, [a.absolute_path for a in e.assets])
        self.assertIn(DEFAULT_DEMOGRAPHICS_JSON, [a.absolute_path for a in e.assets])
        self.assertDictEqual(demog, e.assets.get_one(filename=os.path.basename(DEFAULT_DEMOGRAPHICS_JSON)).content)

        # Config should be equal for the base simulation and generated
        self.assertDictEqual(config, e.base_simulation.config)
        self.assertDictEqual(config, sim.config)

        # After pre_creation, the demographics filenames will be set on the sim so no more equality
        sim.pre_creation()
        self.assertNotEqual(config["Demographics_Filenames"], sim.config["Demographics_Filenames"])
        # Are the demographics set correctly?
        self.assertEqual(sim.config["Demographics_Filenames"],
                         [os.path.join("demographics", os.path.basename(DEFAULT_DEMOGRAPHICS_JSON))])
        # The rest should be the same
        del config["Demographics_Filenames"]
        del sim.config["Demographics_Filenames"]
        self.set_migrations(config)
        self.assertDictEqual(config, sim.config)

        # The demographics coming from the experiment
        self.assertIsNone(sim.assets.get_one(filename=os.path.basename(DEFAULT_DEMOGRAPHICS_JSON)))
        self.assertIsNotNone(sim.demographics.get_one(filename=os.path.basename(DEFAULT_DEMOGRAPHICS_JSON)))

        # No change for campaigns
        self.assertDictEqual(campaign, sim.campaign)
        self.assertDictEqual(campaign, e.base_simulation.campaign)

    def test_load_files_without_demographics(self):
        e = EMODExperiment.from_files(self.case_name,
                                      eradication_path=DEFAULT_ERADICATION_PATH,
                                      config_path=DEFAULT_CONFIG_PATH,
                                      campaign_path=DEFAULT_CAMPAIGN_JSON)

        with open(DEFAULT_CONFIG_PATH, 'r') as fp:
            config = json.load(fp)["parameters"]
        with open(DEFAULT_CAMPAIGN_JSON, 'r') as fp:
            campaign = json.load(fp)

        self.assertDictEqual(config, e.base_simulation.config)
        self.assertDictEqual(campaign, e.base_simulation.campaign)

    def set_migrations(self, dict):
        dict.update({'Enable_Local_Migration': 0})
        dict.update({'Enable_Air_Migration': 0})
        dict.update({'Enable_Family_Migration': 0})
        dict.update({'Enable_Regional_Migration': 0})
        dict.update({'Enable_Sea_Migration': 0})
        return dict
