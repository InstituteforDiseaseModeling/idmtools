import os
import json
from idmtools_models.dtk import DTKExperiment
from idmtools_model_dtk.defaults import DTKSIR
from idmtools_test.utils.ITestWithPersistence import ITestWithPersistence
from idmtools_test import COMMON_INPUT_PATH

DEFAULT_CONFIG_PATH = os.path.join(COMMON_INPUT_PATH, "files", "config.json")
DEFAULT_CAMPAIGN_JSON = os.path.join(COMMON_INPUT_PATH, "files", "campaign.json")
DEFAULT_DEMOGRAPHICS_JSON = os.path.join(COMMON_INPUT_PATH, "files", "demographics.json")
DEFAULT_ERADICATION_PATH = os.path.join(COMMON_INPUT_PATH, "dtk", "Eradication.exe")


class TestCustomFiles(ITestWithPersistence):

    def setUp(self):
        super().setUp()
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        print(self.case_name)

    def tearDown(self):
        super().tearDown()

    def test_simulation_load_config(self):
        e = DTKExperiment.from_default(self.case_name, default=DTKSIR,
                                       eradication_path=DEFAULT_ERADICATION_PATH)

        e.base_simulation.load_files(config_path=DEFAULT_CONFIG_PATH)

        # Test the content
        with open(DEFAULT_CONFIG_PATH, 'r') as m:
            jt1 = e.base_simulation.config
            jt2 = json.load(m)
            self.assertEqual(json.dumps(jt1, sort_keys=True), json.dumps(jt2['parameters'], sort_keys=True))

        # Test: no changes to default campaign
        jt1 = e.base_simulation.campaign
        jt2 = DTKSIR.campaign()
        self.assertEqual(json.dumps(jt1, sort_keys=True), json.dumps(jt2, sort_keys=True))

        # Test: no changes to default demographics
        jt1 = e.demographics
        jt2 = DTKSIR.demographics()
        self.assertEqual(json.dumps(jt1, sort_keys=True), json.dumps(jt2, sort_keys=True))
        self.assertEqual(e.base_simulation.demographics, {})

    def test_simulation_load_campaign(self):
        e = DTKExperiment.from_default(self.case_name, default=DTKSIR,
                                       eradication_path=DEFAULT_ERADICATION_PATH)

        e.base_simulation.load_files(campaign_path=DEFAULT_CAMPAIGN_JSON)

        # Test the content
        with open(DEFAULT_CAMPAIGN_JSON, 'r') as m:
            jt1 = e.base_simulation.campaign
            jt2 = json.load(m)
            self.assertEqual(json.dumps(jt1, sort_keys=True), json.dumps(jt2, sort_keys=True))

        # Test: no changes to default config
        jt1 = e.base_simulation.config
        jt2 = DTKSIR.config()
        self.assertEqual(json.dumps(jt1, sort_keys=True), json.dumps(jt2, sort_keys=True))

        # Test: no changes to default demographics
        jt1 = e.demographics
        jt2 = DTKSIR.demographics()
        self.assertEqual(json.dumps(jt1, sort_keys=True), json.dumps(jt2, sort_keys=True))

    def test_simulation_load_demographics(self):
        e = DTKExperiment.from_default(self.case_name, default=DTKSIR, eradication_path=DEFAULT_ERADICATION_PATH)

        e.base_simulation.load_files(demographics_paths=DEFAULT_DEMOGRAPHICS_JSON)

        # Test the content
        with open(DEFAULT_DEMOGRAPHICS_JSON, 'r') as m:
            jt1 = list(e.base_simulation.demographics.values())[0]
            jt2 = json.load(m)
            self.assertEqual(json.dumps(jt1, sort_keys=True), json.dumps(jt2, sort_keys=True))

        # Test: no changes to default config
        jt1 = e.base_simulation.config
        jt2 = DTKSIR.config()
        jt1.pop("Demographics_Filenames")
        jt2.pop("Demographics_Filenames")
        self.assertEqual(json.dumps(jt1, sort_keys=True), json.dumps(jt2, sort_keys=True))

        # Test: no changes to default campaign
        jt1 = e.base_simulation.campaign
        jt2 = DTKSIR.campaign()
        self.assertEqual(json.dumps(jt1, sort_keys=True), json.dumps(jt2, sort_keys=True))

    def test_simulation_load_files(self):
        e = DTKExperiment.from_default(self.case_name, default=DTKSIR,
                                       eradication_path=DEFAULT_ERADICATION_PATH)

        e.base_simulation.load_files(config_path=DEFAULT_CONFIG_PATH, campaign_path=DEFAULT_CAMPAIGN_JSON,
                                     demographics_paths=DEFAULT_DEMOGRAPHICS_JSON)

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
            jt1 = list(e.base_simulation.demographics.values())[0]
            jt2 = json.load(m)
            self.assertEqual(json.dumps(jt1, sort_keys=True), json.dumps(jt2, sort_keys=True))

    def test_experiment_load_files(self):
        e = DTKExperiment.from_default(self.case_name, default=DTKSIR,
                                       eradication_path=DEFAULT_ERADICATION_PATH)

        e.load_files(config_path=DEFAULT_CONFIG_PATH, campaign_path=DEFAULT_CAMPAIGN_JSON,
                     demographics_paths=DEFAULT_DEMOGRAPHICS_JSON)

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
            jt1 = list(e.demographics.values())[1]
            jt2 = json.load(m)
            self.assertEqual(json.dumps(jt1, sort_keys=True), json.dumps(jt2, sort_keys=True))

    def test_load_from_files(self):
        e = DTKExperiment.from_files(self.case_name,
                                     eradication_path=DEFAULT_ERADICATION_PATH,
                                     config_path=DEFAULT_CONFIG_PATH,
                                     campaign_path=DEFAULT_CAMPAIGN_JSON,
                                     demographics_paths=DEFAULT_DEMOGRAPHICS_JSON
                                     )

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
            jt1 = list(e.demographics.values())[0]
            jt2 = json.load(m)
            self.assertEqual(json.dumps(jt1, sort_keys=True), json.dumps(jt2, sort_keys=True))

    def test_experiment_load_multiple_demographics_files_1(self):
        e = DTKExperiment.from_default(self.case_name, default=DTKSIR,
                                       eradication_path=DEFAULT_ERADICATION_PATH)
        e.load_files(demographics_paths=DEFAULT_DEMOGRAPHICS_JSON)

        # test number of files
        self.assertEqual(len(e.base_simulation.demographics), 0)
        self.assertEqual(len(e.demographics), 2)

        # test the order of files
        demographics_list = list(e.demographics.keys())
        self.assertEqual(demographics_list[1], 'demographics.json')

    def test_experiment_load_multiple_demographics_files_2(self):
        e = DTKExperiment.from_files(self.case_name,
                                     eradication_path=DEFAULT_ERADICATION_PATH,
                                     demographics_paths=[DEFAULT_DEMOGRAPHICS_JSON])

        # test number of files
        self.assertEqual(len(e.base_simulation.demographics), 0)
        self.assertEqual(len(e.demographics), 1)

        # test the order of files
        demographics_list = list(e.demographics.keys())
        self.assertEqual(demographics_list[0], 'demographics.json')

    def test_simulation_load_multiple_demographics_files(self):
        e = DTKExperiment.from_default(self.case_name, default=DTKSIR,
                                       eradication_path=DEFAULT_ERADICATION_PATH)

        e.base_simulation.load_files(demographics_paths=DEFAULT_DEMOGRAPHICS_JSON)
        e.base_simulation.load_files(demographics_paths=DEFAULT_DEMOGRAPHICS_JSON)

        # test number of files
        self.assertEqual(len(e.base_simulation.demographics), 1)
        self.assertEqual(len(e.demographics), 1)

        # test the order of files
        demographics_list = list(e.base_simulation.demographics.keys())
        self.assertEqual(demographics_list[0], 'demographics.json')
