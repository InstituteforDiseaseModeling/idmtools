import json
import os

from idmtools_model_emod import EMODExperiment
from idmtools_model_emod.defaults import EMODSir
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence

DEFAULT_CONFIG_PATH = os.path.join(COMMON_INPUT_PATH, "files", "config.json")
DEFAULT_CAMPAIGN_JSON = os.path.join(COMMON_INPUT_PATH, "files", "campaign.json")
DEFAULT_DEMOGRAPHICS_JSON = os.path.join(COMMON_INPUT_PATH, "files", "demographics.json")
DEFAULT_ERADICATION_PATH = os.path.join(COMMON_INPUT_PATH, "emod", "Eradication.exe")


class TestLoadFiles(ITestWithPersistence):

    def setUp(self):
        super().setUp()
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        print(self.case_name)

    def tearDown(self):
        super().tearDown()

    def test_simulation_load_config(self):
        e = EMODExperiment.from_default(self.case_name, default=EMODSir,
                                        eradication_path=DEFAULT_ERADICATION_PATH)

        e.base_simulation.load_files(config_path=DEFAULT_CONFIG_PATH)
        s = e.simulation()
        e.pre_creation()
        s.pre_creation()

        # Test the content
        with open(DEFAULT_CONFIG_PATH, 'r') as m:
            jt1 = e.base_simulation.config
            jt2 = json.load(m)
            self.assertEqual(json.dumps(jt1, sort_keys=True), json.dumps(jt2['parameters'], sort_keys=True))

        # Test: no changes to default campaign
        jt1 = s.campaign
        jt2 = EMODSir.campaign()
        self.assertEqual(json.dumps(jt1, sort_keys=True), json.dumps(jt2, sort_keys=True))

        # Test: no changes to default demographics
        jt1 = s.demographics[0].content
        jt2 = list(EMODSir.demographics().values())[0]
        self.assertEqual(json.dumps(jt1, sort_keys=True), json.dumps(jt2, sort_keys=True))
        self.assertEqual(s.demographics[0].content, jt1)
        self.assertEqual(len([d for d in s.demographics if not d.persisted]), 0)

    def test_simulation_load_campaign(self):
        e = EMODExperiment.from_default(self.case_name, default=EMODSir,
                                        eradication_path=DEFAULT_ERADICATION_PATH)

        e.base_simulation.load_files(campaign_path=DEFAULT_CAMPAIGN_JSON)

        # Test the content
        with open(DEFAULT_CAMPAIGN_JSON, 'r') as m:
            jt1 = e.base_simulation.campaign
            jt2 = json.load(m)
            self.assertEqual(json.dumps(jt1, sort_keys=True), json.dumps(jt2, sort_keys=True))

        # Test: no changes to default config
        jt1 = e.base_simulation.config
        jt2 = EMODSir.config()
        self.assertEqual(json.dumps(jt1, sort_keys=True), json.dumps(jt2, sort_keys=True))

        # Test: no changes to default demographics
        jt1 = e.demographics[0].content
        jt2 = list(EMODSir.demographics().values())[0]
        self.assertEqual(json.dumps(jt1, sort_keys=True), json.dumps(jt2, sort_keys=True))

    def test_simulation_load_demographics(self):
        e = EMODExperiment.from_default(self.case_name, default=EMODSir, eradication_path=DEFAULT_ERADICATION_PATH)
        e.base_simulation.demographics.add_demographics_from_file(DEFAULT_DEMOGRAPHICS_JSON)

        # Test the content
        with open(DEFAULT_DEMOGRAPHICS_JSON, 'r') as m:
            jt1 = e.base_simulation.demographics[0].content
            jt2 = json.load(m)
            self.assertEqual(json.dumps(jt1, sort_keys=True), json.dumps(jt2, sort_keys=True))

        # Test: no changes to default config
        jt1 = e.base_simulation.config
        jt2 = EMODSir.config()
        jt1.pop("Demographics_Filenames")
        jt2.pop("Demographics_Filenames")
        self.assertEqual(json.dumps(jt1, sort_keys=True), json.dumps(jt2, sort_keys=True))

        # Test: no changes to default campaign
        jt1 = e.base_simulation.campaign
        jt2 = EMODSir.campaign()
        self.assertEqual(json.dumps(jt1, sort_keys=True), json.dumps(jt2, sort_keys=True))

    def test_simulation_load_files(self):
        e = EMODExperiment.from_default(self.case_name, default=EMODSir,
                                        eradication_path=DEFAULT_ERADICATION_PATH)

        e.base_simulation.load_files(config_path=DEFAULT_CONFIG_PATH, campaign_path=DEFAULT_CAMPAIGN_JSON)
        e.base_simulation.demographics.add_demographics_from_file(DEFAULT_DEMOGRAPHICS_JSON)

        # Test the contents
        with open(DEFAULT_CONFIG_PATH, 'r') as m:
            jt1 = e.base_simulation.config
            jt2 = json.load(m)
            jt1.pop("Demographics_Filenames")
            jt2['parameters'].pop("Demographics_Filenames")
            self.assertEqual(json.dumps(jt1, sort_keys=True), json.dumps(jt2['parameters'], sort_keys=True))

        with open(DEFAULT_CAMPAIGN_JSON, 'r') as m:
            jt1 = e.base_simulation.campaign
            jt2 = json.load(m)
            self.assertEqual(json.dumps(jt1, sort_keys=True), json.dumps(jt2, sort_keys=True))

        with open(DEFAULT_DEMOGRAPHICS_JSON, 'r') as m:
            jt1 = e.base_simulation.demographics[0].content
            jt2 = json.load(m)
            self.assertEqual(json.dumps(jt1, sort_keys=True), json.dumps(jt2, sort_keys=True))

    def test_experiment_load_files(self):
        e = EMODExperiment.from_default(self.case_name, default=EMODSir,
                                        eradication_path=DEFAULT_ERADICATION_PATH)
        e.base_simulation.load_files(config_path=DEFAULT_CONFIG_PATH, campaign_path=DEFAULT_CAMPAIGN_JSON)
        e.demographics.add_demographics_from_file(DEFAULT_DEMOGRAPHICS_JSON)

        e.pre_creation()
        s = e.simulation()
        s.pre_creation()

        # Test the contents
        with open(DEFAULT_CONFIG_PATH, 'r') as m:
            jt1 = s.config
            jt2 = json.load(m)
            jt1.pop("Demographics_Filenames")
            jt2['parameters'].pop("Demographics_Filenames")
            jt2 = self.set_migrations(jt2)
            self.assertEqual(json.dumps(jt1, sort_keys=True), json.dumps(jt2['parameters'], sort_keys=True))

        with open(DEFAULT_CAMPAIGN_JSON, 'r') as m:
            jt1 = s.campaign
            jt2 = json.load(m)
            self.assertEqual(json.dumps(jt1, sort_keys=True), json.dumps(jt2, sort_keys=True))

        with open(DEFAULT_DEMOGRAPHICS_JSON, 'r') as m:
            jt1 = s.demographics[1].content
            jt2 = json.load(m)
            self.assertEqual(json.dumps(jt1, sort_keys=True), json.dumps(jt2, sort_keys=True))

    def test_load_from_files(self):
        e = EMODExperiment.from_files(self.case_name,
                                      eradication_path=DEFAULT_ERADICATION_PATH,
                                      config_path=DEFAULT_CONFIG_PATH,
                                      campaign_path=DEFAULT_CAMPAIGN_JSON,
                                      demographics_paths=DEFAULT_DEMOGRAPHICS_JSON
                                      )

        e.pre_creation()
        s = e.simulation()
        s.pre_creation()
        # Test the contents
        with open(DEFAULT_CONFIG_PATH, 'r') as m:
            jt1 = s.config
            jt2 = json.load(m)
            jt1.pop("Demographics_Filenames")
            jt2['parameters'].pop("Demographics_Filenames")
            jt2 = self.set_migrations(jt2)
            self.assertEqual(json.dumps(jt1, sort_keys=True), json.dumps(jt2['parameters'], sort_keys=True))

        with open(DEFAULT_CAMPAIGN_JSON, 'r') as m:
            jt1 = s.campaign
            jt2 = json.load(m)
            self.assertEqual(json.dumps(jt1, sort_keys=True), json.dumps(jt2, sort_keys=True))

        with open(DEFAULT_DEMOGRAPHICS_JSON, 'r') as m:
            jt1 = e.demographics[0].content
            jt2 = json.load(m)
            self.assertEqual(json.dumps(jt1, sort_keys=True), json.dumps(jt2, sort_keys=True))

    def test_experiment_load_multiple_demographics_files_1(self):
        e = EMODExperiment.from_default(self.case_name, default=EMODSir,
                                        eradication_path=DEFAULT_ERADICATION_PATH)
        e.demographics.add_demographics_from_file(DEFAULT_DEMOGRAPHICS_JSON)

        # test number of files
        self.assertEqual(len(e.base_simulation.demographics), 0)
        self.assertEqual(len(e.demographics), 2)

        # test the order of files
        demographics_list = [d.filename for d in e.demographics]
        self.assertEqual(demographics_list[1], 'demographics.json')

    def test_experiment_load_multiple_demographics_files_2(self):
        e = EMODExperiment.from_files(self.case_name,
                                      eradication_path=DEFAULT_ERADICATION_PATH,
                                      demographics_paths=[DEFAULT_DEMOGRAPHICS_JSON])

        # test number of files
        self.assertEqual(len(e.base_simulation.demographics), 0)
        self.assertEqual(len(e.demographics), 1)

        # test the order of files
        demographics_list = [d.filename for d in e.demographics]
        self.assertEqual(demographics_list[0], 'demographics.json')

    def test_simulation_load_multiple_demographics_files(self):
        e = EMODExperiment.from_default(self.case_name, default=EMODSir,
                                        eradication_path=DEFAULT_ERADICATION_PATH)

        e.base_simulation.demographics.add_demographics_from_file(DEFAULT_DEMOGRAPHICS_JSON)

        with self.assertRaises(Exception):
            e.base_simulation.demographics.add_demographics_from_file(DEFAULT_DEMOGRAPHICS_JSON)

        # test number of files
        self.assertEqual(len(e.base_simulation.demographics), 1)
        self.assertEqual(len(e.demographics), 1)

        # test the order of files
        demographics_list = [d.filename for d in e.base_simulation.demographics]
        self.assertEqual(demographics_list[0], 'demographics.json')

    def set_migrations(self, dict):
        dict['parameters'].update({'Enable_Local_Migration': 0})
        dict['parameters'].update({'Enable_Air_Migration': 0})
        dict['parameters'].update({'Enable_Family_Migration': 0})
        dict['parameters'].update({'Enable_Regional_Migration': 0})
        dict['parameters'].update({'Enable_Sea_Migration': 0})
        return dict

