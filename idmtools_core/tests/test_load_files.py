import os
import json
from idmtools_models.dtk import DTKExperiment
from idmtools_models.dtk.defaults import DTKSIR
from idmtools_test.utils.ITestWithPersistence import ITestWithPersistence
from idmtools_test import COMMON_INPUT_PATH

current_directory = os.path.dirname(os.path.realpath(__file__))


class TestCustomFiles(ITestWithPersistence):

    def setUp(self):
        super().setUp()
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        print(self.case_name)

    def tearDown(self):
        super().tearDown()

    def test_simulation_load_config(self):
        e = DTKExperiment.from_default(self.case_name, default=DTKSIR,
                                       eradication_path=os.path.join(COMMON_INPUT_PATH, "dtk", "Eradication.exe"))

        e.base_simulation.load_files(config_path="./inputs/files/config.json")

        # Test the content
        with open("./inputs/files/config.json", 'r') as m:
            jt1 = e.base_simulation.config
            jt2 = json.load(m)
            self.assertEqual(json.dumps(jt1, sort_keys=True), json.dumps(jt2, sort_keys=True))

        # Test: no changes to default campaign
        jt1 = e.base_simulation.campaign
        jt2 = DTKSIR.campaign()
        self.assertEqual(json.dumps(jt1, sort_keys=True), json.dumps(jt2, sort_keys=True))

        # Test: no changes to default demographics
        jt1 = e.base_simulation.demographics
        jt2 = DTKSIR.demographics()
        self.assertEqual(json.dumps(jt1, sort_keys=True), json.dumps(jt2, sort_keys=True))

    def test_simulation_load_campaign(self):
        e = DTKExperiment.from_default(self.case_name, default=DTKSIR,
                                       eradication_path=os.path.join(COMMON_INPUT_PATH, "dtk", "Eradication.exe"))

        e.base_simulation.load_files(campaign_path="./inputs/files/campaign.json")

        # Test the content
        with open("./inputs/files/campaign.json", 'r') as m:
            jt1 = e.base_simulation.campaign
            jt2 = json.load(m)
            self.assertEqual(json.dumps(jt1, sort_keys=True), json.dumps(jt2, sort_keys=True))

        # Test: no changes to default config
        jt1 = e.base_simulation.config
        jt2 = DTKSIR.config()
        self.assertEqual(json.dumps(jt1, sort_keys=True), json.dumps(jt2, sort_keys=True))

        # Test: no changes to default demographics
        jt1 = e.base_simulation.demographics
        jt2 = DTKSIR.demographics()
        self.assertEqual(json.dumps(jt1, sort_keys=True), json.dumps(jt2, sort_keys=True))

    def test_simulation_load_demographics(self):
        e = DTKExperiment.from_default(self.case_name, default=DTKSIR,
                                       eradication_path=os.path.join(COMMON_INPUT_PATH, "dtk", "Eradication.exe"))

        e.base_simulation.load_files(demographics_path="./inputs/files/demographics.json")

        # Test the content
        with open("./inputs/files/demographics.json", 'r') as m:
            jt1 = e.base_simulation.demographics
            jt2 = json.load(m)
            self.assertEqual(json.dumps(jt1, sort_keys=True), json.dumps(jt2, sort_keys=True))

        # Test: no changes to default config
        jt1 = e.base_simulation.config
        jt2 = DTKSIR.config()
        self.assertEqual(json.dumps(jt1, sort_keys=True), json.dumps(jt2, sort_keys=True))

        # Test: no changes to default campaign
        jt1 = e.base_simulation.campaign
        jt2 = DTKSIR.campaign()
        self.assertEqual(json.dumps(jt1, sort_keys=True), json.dumps(jt2, sort_keys=True))

    def test_simulation_load_files(self):
        e = DTKExperiment.from_default(self.case_name, default=DTKSIR,
                                       eradication_path=os.path.join(COMMON_INPUT_PATH, "dtk", "Eradication.exe"))

        e.base_simulation.load_files(config_path="./inputs/files/config.json",
                                     campaign_path="./inputs/files/campaign.json",
                                     demographics_path="./inputs/files/demographics.json")

        # Test the contents
        with open("./inputs/files/config.json", 'r') as m:
            jt1 = e.base_simulation.config
            jt2 = json.load(m)
            self.assertEqual(json.dumps(jt1, sort_keys=True), json.dumps(jt2, sort_keys=True))

        with open("./inputs/files/campaign.json", 'r') as m:
            jt1 = e.base_simulation.campaign
            jt2 = json.load(m)
            self.assertEqual(json.dumps(jt1, sort_keys=True), json.dumps(jt2, sort_keys=True))

        with open("./inputs/files/demographics.json", 'r') as m:
            jt1 = e.base_simulation.demographics
            jt2 = json.load(m)
            self.assertEqual(json.dumps(jt1, sort_keys=True), json.dumps(jt2, sort_keys=True))

    def test_experiment_load_files(self):
        e = DTKExperiment.from_default(self.case_name, default=DTKSIR,
                                       eradication_path=os.path.join(COMMON_INPUT_PATH, "dtk", "Eradication.exe"))

        e.load_files(config_path="./inputs/files/config.json",
                     campaign_path="./inputs/files/campaign.json",
                     demographics_path="./inputs/files/demographics.json")

        # Test the contents
        with open("./inputs/files/config.json", 'r') as m:
            jt1 = e.base_simulation.config
            jt2 = json.load(m)
            self.assertEqual(json.dumps(jt1, sort_keys=True), json.dumps(jt2, sort_keys=True))

        with open("./inputs/files/campaign.json", 'r') as m:
            jt1 = e.base_simulation.campaign
            jt2 = json.load(m)
            self.assertEqual(json.dumps(jt1, sort_keys=True), json.dumps(jt2, sort_keys=True))

        with open("./inputs/files/demographics.json", 'r') as m:
            jt1 = e.base_simulation.demographics
            jt2 = json.load(m)
            self.assertEqual(json.dumps(jt1, sort_keys=True), json.dumps(jt2, sort_keys=True))

    def test_load_from_files(self):
        e = DTKExperiment.from_files(self.case_name,
                                     eradication_path=os.path.join(COMMON_INPUT_PATH, "dtk", "Eradication.exe"),
                                     config_path="./inputs/files/config.json",
                                     campaign_path="./inputs/files/campaign.json",
                                     demographics_path="./inputs/files/demographics.json")

        # Test the contents
        with open("./inputs/files/config.json", 'r') as m:
            jt1 = e.base_simulation.config
            jt2 = json.load(m)
            self.assertEqual(json.dumps(jt1, sort_keys=True), json.dumps(jt2, sort_keys=True))

        with open("./inputs/files/campaign.json", 'r') as m:
            jt1 = e.base_simulation.campaign
            jt2 = json.load(m)
            self.assertEqual(json.dumps(jt1, sort_keys=True), json.dumps(jt2, sort_keys=True))

        with open("./inputs/files/demographics.json", 'r') as m:
            jt1 = e.base_simulation.demographics
            jt2 = json.load(m)
            self.assertEqual(json.dumps(jt1, sort_keys=True), json.dumps(jt2, sort_keys=True))
