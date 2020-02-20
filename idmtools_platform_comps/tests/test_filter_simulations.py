import os
import unittest
from functools import partial

from idmtools.core import ItemType, EntityStatus
from idmtools.core.platform_factory import Platform
from idmtools.entities import Suite
from idmtools.managers import ExperimentManager
from idmtools.utils.filter_simulations import FilterItem

from idmtools_models.python import PythonExperiment
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools.builders import ExperimentBuilder


class TestSimulations(ITestWithPersistence):

    def _run_create_test_experiments(self):
        """
        create suite and experiment with 5 simulations. 2 succeed ones and 3 failed ones
        :return: ExperimentManager
        """
        def param_update(simulation, param, value):
            return simulation.set_parameter(param, value)
        setA = partial(param_update, param="Run_Number")

        experiment = PythonExperiment(name="test_experiments",
                                      model_path=os.path.join(COMMON_INPUT_PATH, "python_experiments", "model.py"))
        builder = ExperimentBuilder()
        builder.add_sweep_definition(setA, range(5))

        experiment.add_builder(builder)

        suite = Suite(name='Idm Suite')
        suite.update_tags({'name': 'test', 'fetch': 123})
        em = ExperimentManager(platform=self.platform, experiment=experiment, suite=suite)
        em.run()
        em.wait_till_done()
        return em

    @classmethod
    def setUpClass(cls):
        cls.platform = Platform('COMPS2')
        em: ExperimentManager = cls._run_create_test_experiments(cls)
        cls.experiment = em.experiment
        cls.suite = em.suite

    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        print(self.case_name)

    # Filter from Experiment, self.experiment has 5 simulations includes 2 succeed sims and 3 failed sims
    # Test default filter with experiment uuid and type which only returns succeed sims (2 in this case)
    def test_filter_experiment(self):
        sims = FilterItem.filter_item_by_id(self.platform, self.experiment.uid, ItemType.EXPERIMENT, max_simulations=5)
        self.assertEqual(len(sims), 2)

    # Filer from Suite
    # Test default filter with suite uuid and type which only returns succeed sims (2 in this case)
    def test_filter_suite(self):
        sims = FilterItem.filter_item_by_id(self.platform, self.suite.uid, ItemType.SUITE)
        self.assertEqual(len(sims), 2)

    # Test default filter plus tags which only returns 1 matched succeed sims
    def test_filter_item_experiment(self):
        exp = self.platform.get_item(self.experiment.uid, ItemType.EXPERIMENT, raw=False)
        sims = FilterItem.filter_item(self.platform, exp, max_simulations=5, tags={'Run_Number': '1'})
        self.assertEqual(len(sims), 1)

    # test filter with suite which only return succeed sims by default
    def test_filter_item_suite(self):
        suite = self.platform.get_item(self.suite.uid, ItemType.SUITE, raw=False)
        sims = FilterItem.filter_item(self.platform, suite)
        self.assertEqual(len(sims), 2)

    # test filter with experiment and status=failed which only return failed sims(3 in this case)
    def test_filter_item_experiment_status(self):
        exp = self.platform.get_item(self.experiment.uid, ItemType.EXPERIMENT, raw=False)
        sims = FilterItem.filter_item(self.platform, exp, max_simulations=5, status=EntityStatus.FAILED)
        self.assertEqual(len(sims), 3)

    # test filter with experiment and tags which only return 1 matched succeed sim
    def test_filter_item_experiment_tags(self):
        exp = self.platform.get_item(self.experiment.uid, ItemType.EXPERIMENT, raw=False)
        sims = FilterItem.filter_item(self.platform, exp, max_simulations=5, tags={'Run_Number': '1'})
        self.assertEqual(len(sims), 1)

    # test filter with experiment and max_simulations filter which only return 1 matched succeed sim
    def test_filter_item_experiment_max(self):
        exp = self.platform.get_item(self.experiment.uid, ItemType.EXPERIMENT, raw=False)
        sims = FilterItem.filter_item(self.platform, exp, max_simulations=1)
        self.assertEqual(len(sims), 1)

    # test filter with experiment and skip_sims filter which only return 1 matched succeed sim (another one skipped)
    def test_filter_experiment_skip(self):
        # Filter from Experiment
        skip_sim = str(self.experiment.simulations[1].uid)
        sims = FilterItem.filter_item_by_id(self.platform, self.experiment.uid, ItemType.EXPERIMENT,
                                            skip_sims=[skip_sim], max_simulations=5)
        self.assertEqual(len(sims), 1)


if __name__ == '__main__':
    unittest.main()
