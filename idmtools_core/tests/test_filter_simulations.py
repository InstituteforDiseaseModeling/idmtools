import os
import unittest
from idmtools.core import ItemType, EntityStatus
from idmtools.core.platform_factory import Platform
from idmtools.utils.filter_simulations import FilterItem
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence


class TestSimulations(ITestWithPersistence):

    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        print(self.case_name)
        self.platform = Platform('COMPS2')

    def test_filter_experiment(self):
        # Filter from Experiment
        exp_id = '06da767c-f249-ea11-a2be-f0921c167861'  # 2/5 succeed
        sims = FilterItem.filter_item_by_id(self.platform, exp_id, ItemType.EXPERIMENT, max_simulations=5)
        self.assertEqual(len(sims), 2)

    def test_filter_suite(self):
        # Filer from Suite
        suite_id = '502b6f0c-2920-ea11-a2be-f0921c167861'  # comps2 staging exp id
        sims = FilterItem.filter_item_by_id(self.platform, suite_id, ItemType.SUITE)
        self.assertEqual(len(sims), 3)

    def test_filter_item_experiment(self):
        exp_id = '06da767c-f249-ea11-a2be-f0921c167861'  # 2/5 succeed

        exp = self.platform.get_item(exp_id, ItemType.EXPERIMENT, raw=False)
        sims = FilterItem.filter_item(self.platform, exp, max_simulations=5, tags={'Run_Number': '2'})
        self.assertEqual(len(sims), 1)

    def test_filter_item_suite(self):
        suite_id = '502b6f0c-2920-ea11-a2be-f0921c167861'  # comps2 staging exp id

        suite = self.platform.get_item(suite_id, ItemType.SUITE, raw=False)
        sims = FilterItem.filter_item(self.platform, suite)
        self.assertEqual(len(sims), 3)

    def test_filter_item_experiment_status(self):
        exp_id = '06da767c-f249-ea11-a2be-f0921c167861'  # 2/5 succeed

        exp = self.platform.get_item(exp_id, ItemType.EXPERIMENT, raw=False)
        sims = FilterItem.filter_item(self.platform, exp, max_simulations=5, status=EntityStatus.CREATED)
        self.assertEqual(len(sims), 3)

    def test_filter_item_experiment_tags(self):
        exp_id = '06da767c-f249-ea11-a2be-f0921c167861'  # 2/5 succeed

        exp = self.platform.get_item(exp_id, ItemType.EXPERIMENT, raw=False)
        sims = FilterItem.filter_item(self.platform, exp, max_simulations=5, tags={'Run_Number': '2'})
        self.assertEqual(len(sims), 1)

    def test_filter_item_experiment_max(self):
        exp_id = '06da767c-f249-ea11-a2be-f0921c167861'  # 2/5 succeed

        exp = self.platform.get_item(exp_id, ItemType.EXPERIMENT, raw=False)
        sims = FilterItem.filter_item(self.platform, exp, max_simulations=1)
        self.assertEqual(len(sims), 1)


if __name__ == '__main__':
    unittest.main()
