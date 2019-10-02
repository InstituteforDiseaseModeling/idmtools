import os
import copy
from idmtools_model_emod.defaults import EMODSir
from idmtools_model_emod import EMODExperiment
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools_test import COMMON_INPUT_PATH

DEFAULT_CONFIG_PATH = os.path.join(COMMON_INPUT_PATH, "files", "config.json")
DEFAULT_CAMPAIGN_JSON = os.path.join(COMMON_INPUT_PATH, "files", "campaign.json")
DEFAULT_DEMOGRAPHICS_JSON = os.path.join(COMMON_INPUT_PATH, "files", "demographics.json")
DEFAULT_ERADICATION_PATH = os.path.join(COMMON_INPUT_PATH, "dtk", "Eradication.exe")


class TestCopy(ITestWithPersistence):

    def setUp(self):
        super().setUp()
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        print(self.case_name)

    def tearDown(self):
        super().tearDown()

    def test_deepcopy_assets(self):
        e = EMODExperiment.from_default(self.case_name, default=EMODSir,
                                       eradication_path=DEFAULT_ERADICATION_PATH)

        e.load_files(config_path=DEFAULT_CONFIG_PATH, campaign_path=DEFAULT_CAMPAIGN_JSON,
                     demographics_paths=DEFAULT_DEMOGRAPHICS_JSON)

        # test deepcopy of experiment
        e.gather_assets()
        ep = copy.deepcopy(e)
        self.assertEqual(len(ep.assets.assets), 0)
        ep.assets = copy.deepcopy(e.assets)
        self.assertEqual(len(ep.assets.assets), 2)
        self.assertEqual(e.assets, ep.assets)

        # test deepcopy of simulation
        e.base_simulation.gather_assets()
        sim = copy.deepcopy(e.base_simulation)
        self.assertEqual(len(sim.assets.assets), 0)
        sim.assets = copy.deepcopy(e.base_simulation.assets)
        self.assertEqual(len(sim.assets.assets), 2)
        self.assertEqual(e.base_simulation.assets, sim.assets)
