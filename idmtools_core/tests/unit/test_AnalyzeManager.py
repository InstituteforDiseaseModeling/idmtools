import unittest

from idmtools.analysis.AnalyzeManager import AnalyzeManager
from idmtools.analysis.DownloadAnalyzer import DownloadAnalyzer as SampleAnalyzer
from idmtools.core.enums import EntityStatus
from idmtools.core.ItemId import ItemId
from idmtools.core.PlatformFactory import PlatformFactory
from idmtools.entities.IItem import IItem
from idmtools.entities.IAnalyzer import IAnalyzer


class TestItem(IItem):
    def __init__(self, uid=None):
        super().__init__(_uid=uid)


class TestAnalyzer(IAnalyzer):
    def __init__(self, working_dir=None):
        super().__init__(working_dir=working_dir)
        self.initialize_was_called = False

    def initialize(self):
        self.initialize_was_called = True


class TestAnalyzeManager(unittest.TestCase):

    def _get_analyze_manager(self, ids=None, analyzers=None, working_dir=None, force_wd=False,
                             partial_analyze_ok=False, max_items=None, potential_items=None):
        am = AnalyzeManager(configuration=self.configuration, platform=self.platform,
                            ids=ids, analyzers=analyzers,
                            working_dir=working_dir, force_manager_working_directory=force_wd, verbose=False,
                            partial_analyze_ok=partial_analyze_ok, max_items=max_items)
        if potential_items is not None:  # for use with items that are not real; not in a platform for actual retrieval
            am.potential_items = potential_items
        return am

    def setUp(self) -> None:
        self.configuration = {'max_processes': 2}
        self.platform = PlatformFactory.create(key='COMPS')
        self.analyze_manager = self._get_analyze_manager()
        item_id = ItemId([('simulation_id', '123'), ('experiment_id', '456')])
        self.sample_item = TestItem(uid='abc')
        self.sample_analyzer = SampleAnalyzer()

    # verify add_item() works
    def test_add_item(self):
        self.assertEqual(len(self.analyze_manager.potential_items), 0)
        self.analyze_manager.add_item(item=self.sample_item)
        self.assertEqual(len(self.analyze_manager.potential_items), 1)

    def test_can_analyze_item(self):
        for status in EntityStatus:
            self.sample_item.status = status
            if status == EntityStatus.SUCCEEDED:
                self.assertTrue(AnalyzeManager.can_analyze_item(item=self.sample_item))
            else:
                self.assertFalse(AnalyzeManager.can_analyze_item(item=self.sample_item))

    # check the conditionals; do they work properly when partial_analyze_ok and/or max_items_to_analyze are used?
    def test_get_items_to_analyze(self):
        # first make sure that partial analyze is set to True if max_items has been specified
        am = self._get_analyze_manager(partial_analyze_ok=False, max_items=None)
        self.assertFalse(am.partial_analyze_ok)
        am = self._get_analyze_manager(partial_analyze_ok=True, max_items=None)
        self.assertTrue(am.partial_analyze_ok)

        am = self._get_analyze_manager(partial_analyze_ok=False, max_items=1)
        self.assertTrue(am.partial_analyze_ok)  # overridden by max_items setting
        am = self._get_analyze_manager(partial_analyze_ok=True, max_items=1)
        self.assertTrue(am.partial_analyze_ok)

        #
        # set up 3 item set cases for subsequent tests/asserts: all ready, none ready, some ready
        #

        item_sets = {}
        all_ready = 'all'
        none_ready = 'none'
        some_ready = 'some'

        # all ready
        items = [TestItem(uid=i) for i in range(2)]
        for item in items:
            item.status = EntityStatus.SUCCEEDED
        item_sets[all_ready] = items

        # none ready
        items = [TestItem(uid=i) for i in range(2)]
        for item in items:
            item.status = EntityStatus.FAILED
        item_sets[none_ready] = items

        # some ready
        items = [TestItem(uid=i) for i in range(2)]
        items[0].status = EntityStatus.RUNNING
        items[1].status = EntityStatus.SUCCEEDED
        item_sets[some_ready] = items

        #
        # check returned items when all of them are ready
        #

        test = all_ready
        item_set = item_sets[test]
        # We will be tricking the asset manager by self-supplying the objects for analyzing; they don't exist in a
        # platform for real retrieval.

        # test partial_ok True
        am = self._get_analyze_manager(ids=None, partial_analyze_ok=True, potential_items=item_set)
        items_to_analyze = am._get_items_to_analyze()
        self.assertEqual(len(items_to_analyze), 2)
        self.assertEqual(set(items_to_analyze.keys()), {item.uid for item in item_set if item.status == EntityStatus.SUCCEEDED})

        # test partial_ok False
        am = self._get_analyze_manager(ids=None, partial_analyze_ok=False, potential_items=item_set)
        items_to_analyze = am._get_items_to_analyze()
        self.assertEqual(len(items_to_analyze), 2)
        self.assertEqual(set(items_to_analyze.keys()), {item.uid for item in item_set if item.status == EntityStatus.SUCCEEDED})

        # test max_items 1
        am = self._get_analyze_manager(ids=None, max_items=1, potential_items=item_set)
        items_to_analyze = am._get_items_to_analyze()
        self.assertEqual(len(items_to_analyze), 1)
        # we don't know which successful items were actually returned
        potential_items_uids = {item.uid for item in item_set if item.status == EntityStatus.SUCCEEDED}
        for actual_item_uid in items_to_analyze.keys():
            self.assertTrue(actual_item_uid in potential_items_uids)

        #
        # check returned items when none of them are ready
        #

        test = none_ready
        item_set = item_sets[test]

        # test partial_ok True
        am = self._get_analyze_manager(ids=None, partial_analyze_ok=True, potential_items=item_set)
        items_to_analyze = am._get_items_to_analyze()
        self.assertEqual(len(items_to_analyze), 0)
        self.assertEqual(set(items_to_analyze.keys()), {item.uid for item in item_set if item.status == EntityStatus.SUCCEEDED})

        # test partial_ok False
        am = self._get_analyze_manager(ids=None, partial_analyze_ok=False, potential_items=item_set)
        self.assertRaises(AnalyzeManager.ItemsNotReady, am._get_items_to_analyze)

        # test max_items 1
        am = self._get_analyze_manager(ids=None, max_items=1, potential_items=item_set)
        items_to_analyze = am._get_items_to_analyze()
        self.assertEqual(len(items_to_analyze), 0)

        #
        # check returned items when some (not all) of them are ready
        #

        test = some_ready
        item_set = item_sets[test]

        # test partial_ok True
        am = self._get_analyze_manager(ids=None, partial_analyze_ok=True, potential_items=item_set)
        items_to_analyze = am._get_items_to_analyze()
        self.assertEqual(len(items_to_analyze), 1)
        self.assertEqual(set(items_to_analyze.keys()), {item.uid for item in item_set if item.status == EntityStatus.SUCCEEDED})

        # test partial_ok False
        am = self._get_analyze_manager(ids=None, partial_analyze_ok=False, potential_items=item_set)
        self.assertRaises(AnalyzeManager.ItemsNotReady, am._get_items_to_analyze)

        # test max_items 1
        am = self._get_analyze_manager(ids=None, max_items=1, potential_items=item_set)
        items_to_analyze = am._get_items_to_analyze()
        self.assertEqual(len(items_to_analyze), 1)
        # we don't know which successful items were actually returned, if we had a larger test sample than this
        potential_items_uids = {item.uid for item in item_set if item.status == EntityStatus.SUCCEEDED}
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
        analyzers = [TestAnalyzer() for i in range(3)]
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
                TestAnalyzer(),
                TestAnalyzer(working_dir=analyzer_wd)
            ]
            am = self._get_analyze_manager(analyzers=analyzers, working_dir=analyze_manager_wd, force_wd=force_wd)
            am._initialize_analyzers()
            actual = [analyzer.working_dir for analyzer in am.analyzers]
            self.assertEqual(actual, expected[force_wd])

    # does it properly return t/f for excpetions in the cache?
    def test_check_exception(self):
        self.analyze_manager.cache['random_key'] = 9
        self.assertFalse(self.analyze_manager._check_exception())
        self.analyze_manager.cache[AnalyzeManager.EXCEPTION_KEY] = 'blah'
        self.assertTrue(self.analyze_manager._check_exception())
