import unittest
from typing import Any

import pytest

from idmtools.analysis.AnalyzeManager import AnalyzeManager
from idmtools.analysis.DownloadAnalyzer import DownloadAnalyzer as SampleAnalyzer
from idmtools.builders import StandAloneSimulationsBuilder
from idmtools.core.enums import EntityStatus, ItemType
from idmtools.core.interfaces.iitem import TItem
from idmtools.core.platform_factory import Platform
from idmtools.entities.ianalyzer import IAnalyzer
from idmtools.managers import ExperimentManager
from idmtools_test.utils.tst_experiment import TstExperiment


@pytest.mark.analysis
class TestAnalyzeManager(unittest.TestCase):
    class TestAnalyzer(IAnalyzer):
        def __init__(self, working_dir=None):
            super().__init__(working_dir=working_dir)
            self.initialize_was_called = False

        def initialize(self):
            self.initialize_was_called = True

        def map(self, data: 'Any', item: 'TItem') -> 'Any':
            pass

        def reduce(self, all_data: dict) -> 'Any':
            pass

    def setUp(self) -> None:
        self.platform = Platform('Test')
        self.sample_experiment = TstExperiment()
        em = ExperimentManager(self.sample_experiment, self.platform)
        em.run()
        self.platform.set_simulation_status(self.sample_experiment.uid, status=EntityStatus.SUCCEEDED)
        self.configuration = {'max_processes': 2}

        self.analyze_manager = AnalyzeManager(self.platform)
        self.sample_analyzer = SampleAnalyzer()

    # verify add_item() works
    def test_add_item(self):
        self.assertEqual(len(self.analyze_manager.potential_items), 0)
        self.analyze_manager.add_item(item=self.sample_experiment)
        self.assertEqual(len(self.analyze_manager.potential_items), 1)

    def test_can_analyze_item(self):
        self.analyze_manager.partial_analyze_ok = True
        for status in EntityStatus:
            self.platform.set_simulation_status(self.sample_experiment.uid, status)
            self.analyze_manager.add_item(self.sample_experiment)
            if status == EntityStatus.SUCCEEDED:
                self.assertTrue(len(self.analyze_manager._get_items_to_analyze()) == 1)
            else:
                self.assertTrue(len(self.analyze_manager._get_items_to_analyze()) == 0)

            self.analyze_manager.potential_items.clear()

    # check the conditionals; do they work properly when partial_analyze_ok and/or max_items_to_analyze are used?
    def test_get_items_to_analyze(self):
        # first make sure that partial analyze is set to True if max_items has been specified
        am = AnalyzeManager(self.platform, partial_analyze_ok=False)
        self.assertFalse(am.partial_analyze_ok)
        am = AnalyzeManager(self.platform, partial_analyze_ok=True)
        self.assertTrue(am.partial_analyze_ok)

        am = AnalyzeManager(self.platform, partial_analyze_ok=False, max_items=1)
        self.assertTrue(am.partial_analyze_ok)  # overridden by max_items setting
        am = AnalyzeManager(self.platform, partial_analyze_ok=True, max_items=1)
        self.assertTrue(am.partial_analyze_ok)

        #
        # set up 3 item set cases for subsequent tests/asserts: all ready, none ready, some ready
        #

        results_expected = {'all': (2, 2, 1),
                            'none': (0, None, 0),
                            'some': (1, None, 1)}

        test_exp = TstExperiment()
        b = StandAloneSimulationsBuilder()
        b.add_simulation(test_exp.simulation())
        b.add_simulation(test_exp.simulation())
        em = ExperimentManager(test_exp, self.platform)
        test_exp.builders.add(b)
        em.run()

        # all ready
        for test_name, results in results_expected.items():
            print(f"Testing {test_name}")

            # Fail a few or all
            if test_name == 'all':
                self.platform.set_simulation_status(test_exp.uid, EntityStatus.SUCCEEDED)
            elif test_name == 'none':
                self.platform.set_simulation_status(test_exp.uid, EntityStatus.FAILED)
            else:
                self.platform.set_simulation_status(test_exp.uid, EntityStatus.FAILED)
                self.platform.set_simulation_num_status(test_exp.uid, EntityStatus.SUCCEEDED, 1)

            # test partial_ok True
            am = AnalyzeManager(self.platform, ids=[(test_exp.uid, ItemType.EXPERIMENT)], partial_analyze_ok=True)
            items_to_analyze = am._get_items_to_analyze()
            self.assertEqual(len(items_to_analyze), results[0])
            self.assertEqual(set(items_to_analyze.keys()),
                             {item.uid for item in self.platform.get_children(test_exp.uid, ItemType.EXPERIMENT, force=True) if item.status == EntityStatus.SUCCEEDED})

            # test partial_ok False
            am = AnalyzeManager(self.platform, ids=[(test_exp.uid, ItemType.EXPERIMENT)], partial_analyze_ok=False)
            if results[1]:
                items_to_analyze = am._get_items_to_analyze()
                self.assertEqual(len(items_to_analyze), results[1])
                self.assertEqual(set(items_to_analyze.keys()),
                                 {item.uid for item in
                                  self.platform.get_children(test_exp.uid, ItemType.EXPERIMENT, force=True) if
                                  item.status == EntityStatus.SUCCEEDED})
            else:
                self.assertRaises(AnalyzeManager.ItemsNotReady, am._get_items_to_analyze)

            # test max_items 1
            am = AnalyzeManager(self.platform, ids=[(test_exp.uid, ItemType.EXPERIMENT)], max_items=1)
            items_to_analyze = am._get_items_to_analyze()
            self.assertEqual(len(items_to_analyze), results[2])
            # we don't know which successful items were actually returned
            potential_items_uids = {item.uid for item in self.platform.get_children(test_exp.uid, ItemType.EXPERIMENT, force=True) if item.status == EntityStatus.SUCCEEDED}
            for actual_item_uid in items_to_analyze.keys():
                self.assertTrue(actual_item_uid in potential_items_uids)

    def test_add_analyzer(self):
        self.assertEqual(len(self.analyze_manager.analyzers), 0)
        self.analyze_manager.add_analyzer(analyzer=self.sample_analyzer)
        self.assertEqual(len(self.analyze_manager.analyzers), 1)

    # make sure the uids are unique at the end. Try passing in 1 or > 1 instances of the same analyzer class, too.
    def test_update_analyzer_uids(self):
        self.analyze_manager.add_analyzer(analyzer=SampleAnalyzer())
        self.analyze_manager.add_analyzer(analyzer=SampleAnalyzer())
        self.analyze_manager._update_analyzer_uids()
        unique_uids = {analyzer.uid for analyzer in self.analyze_manager.analyzers}
        self.assertEqual(len(unique_uids), 2)

    # tests of _initialize_analyzers, mostly working_dir setup. Brief check on uid uniqueness by calling the guts of
    # the prior test
    def test_initialize_analyzers(self):
        analyzers = [self.TestAnalyzer() for i in range(3)]
        for analyzer in analyzers:
            self.analyze_manager.add_analyzer(analyzer=analyzer)
        self.analyze_manager._initialize_analyzers()

        # verify each analyzer was initialized
        for analyzer in self.analyze_manager.analyzers:
            self.assertTrue(analyzer.initialize_was_called)

        # verify they have unique uids
        unique_uids = {analyzer.uid for analyzer in self.analyze_manager.analyzers}
        self.assertEqual(len(unique_uids), len(analyzers))

        # verify working dir was set properly
        analyzer_wd = 'fromtheanalyzer'
        analyze_manager_wd = 'fromtheanalyzemanager'

        expected = {
            True: [analyze_manager_wd, analyze_manager_wd],
            False: [analyze_manager_wd, analyzer_wd]
        }
        for force_wd in [True, False]:
            analyzers = [
                self.TestAnalyzer(),
                self.TestAnalyzer(working_dir=analyzer_wd)
            ]
            am = AnalyzeManager(self.platform, analyzers=analyzers, working_dir=analyze_manager_wd,
                                force_manager_working_directory=force_wd)
            am._initialize_analyzers()
            actual = [analyzer.working_dir for analyzer in am.analyzers]
            self.assertEqual(actual, expected[force_wd])

    # does it properly return t/f for excpetions in the cache?
    def test_check_exception(self):
        self.analyze_manager.cache['random_key'] = 9
        self.assertFalse(self.analyze_manager._check_exception())
        self.analyze_manager.cache[AnalyzeManager.EXCEPTION_KEY] = 'blah'
        self.assertTrue(self.analyze_manager._check_exception())
