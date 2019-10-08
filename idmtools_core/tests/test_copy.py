import os
import copy
from functools import partial
from idmtools_model_emod.defaults import EMODSir
from idmtools_model_emod import EMODExperiment
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools_test import COMMON_INPUT_PATH

DEFAULT_CONFIG_PATH = os.path.join(COMMON_INPUT_PATH, "files", "config.json")
DEFAULT_CAMPAIGN_JSON = os.path.join(COMMON_INPUT_PATH, "files", "campaign.json")
DEFAULT_DEMOGRAPHICS_JSON = os.path.join(COMMON_INPUT_PATH, "files", "demographics.json")
DEFAULT_ERADICATION_PATH = os.path.join(COMMON_INPUT_PATH, "dtk", "Eradication.exe")


def param_update(simulation, param, value):
    return simulation.set_parameter(param, value)


class setParam:
    def __init__(self, param):
        self.param = param

    def __call__(self, simulation, value):
        return param_update(simulation, self.param, value)


setA = partial(param_update, param="a")


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

    def test_deepcopy_experiment(self):
        e = EMODExperiment.from_default(self.case_name, default=EMODSir,
                                        eradication_path=DEFAULT_ERADICATION_PATH)

        e.load_files(config_path=DEFAULT_CONFIG_PATH, campaign_path=DEFAULT_CAMPAIGN_JSON,
                     demographics_paths=DEFAULT_DEMOGRAPHICS_JSON)

        from idmtools.builders import ExperimentBuilder
        builder = ExperimentBuilder()
        builder.add_sweep_definition(setA, range(10))
        builder.add_sweep_definition(setParam("b"), [1, 2, 3])

        e.add_builder(builder)

        sim1 = e.simulation()
        sim2 = e.simulation()

        e.simulations.append(sim1)
        e.simulations.append(sim2)

        e.gather_assets()

        self.assertEqual(len(e.builders), 1)
        self.assertEqual(len(e.simulations), 2)
        self.assertEqual(len(e.assets.assets), 2)

        # test deepcopy of experiment
        ep = copy.deepcopy(e)

        self.assertEqual(len(ep.builders), 0)
        self.assertEqual(len(ep.simulations), 0)
        self.assertEqual(len(ep.assets.assets), 0)
        self.assertEqual(e, ep)

        with self.assertRaises(AssertionError) as context:
            self.assertDictEqual(vars(e), vars(ep))
        self.assertIn('Set self.maxDiff to None to see it', context.exception.args[0])

    def test_deepcopy_simulation(self):
        e = EMODExperiment.from_default(self.case_name, default=EMODSir,
                                        eradication_path=DEFAULT_ERADICATION_PATH)

        sim = e.simulation()
        sim.load_files(config_path=DEFAULT_CONFIG_PATH, campaign_path=DEFAULT_CAMPAIGN_JSON,
                       demographics_paths=DEFAULT_DEMOGRAPHICS_JSON)

        sim.gather_assets()

        self.assertEqual(len(sim.assets.assets), 3)
        self.assertIsNotNone(sim.experiment)

        # test deepcopy of simulation
        sp = copy.deepcopy(sim)

        self.assertEqual(len(sp.assets.assets), 0)
        self.assertIsNotNone(sp.experiment)
        self.assertEqual(sim, sp)

        self.assertDictEqual(vars(sim), vars(sp))

    def test_deepcopy_platform(self):
        from idmtools.core.platform_factory import Platform
        p = Platform('COMPS')

        pp = copy.deepcopy(p)
        self.assertEqual(p, pp)
        self.assertDictEqual(vars(p), vars(pp))
