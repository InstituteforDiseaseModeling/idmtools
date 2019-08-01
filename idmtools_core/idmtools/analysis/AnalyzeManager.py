import os
import sys
import time

from idmtools.analysis.map_worker_entry import map_item
from idmtools.core.CacheEnabled import CacheEnabled
from idmtools.core.enums import EntityStatus
from idmtools.utils.command_line import animation
from idmtools.utils.language import on_off, verbose_timedelta
from multiprocessing.pool import Pool

ANALYZE_TIMEOUT = 3600 * 8  # Maximum seconds before timing out - set to 1h
WAIT_TIME = 1.15  # How much time to wait between check if the analysis is done
EXCEPTION_KEY = '__EXCEPTION__'


def pool_worker_initializer(func, analyzers, cache, platform) -> None:
    """
    Initializer function for the process pool.
    Allows the pool to associate the analyzers, cache and path_mapping to the function executed to retrieve data.
    We use an initializer to improve the performances.

    Args:
        func: The function that the pool will call (probably `retrieve_data` here)
        analyzers: The list of all analyzers to run
        cache: The cache object
        platform: The platform to communicate with to retrieve files from

    Returns:

    """
    func.analyzers = analyzers
    func.cache = cache
    func.platform = platform


class AnalyzeManager(CacheEnabled):

    class TimeOutException(Exception):
        pass

    class ItemsNotReady(Exception):
        pass

    def __init__(self, configuration, platform, items=None, analyzers=None, working_dir=os.getcwd(),
                 partial_analyze_ok=False, max_items=None, verbose=True, force_manager_working_directory=False):
        super().__init__()
        self.configuration = configuration
        self.platform = platform
        self.max_processes = min(os.cpu_count(), self.configuration.get('max_processes', 32))

        # analyze at most this many items, regardless of how many have been given
        self.max_items_to_analyze = max_items

        # allows analysis to be performed even if some items are not ready for analysis
        self.partial_analyze_ok = partial_analyze_ok or (self.max_items_to_analyze is not None)

        # Each analyzers results will be in the working_dir directory if not specified by them directly.
        # force_wd overrides this by forcing all results to be in working_dir .
        self.working_dir = working_dir
        self.force_wd = force_manager_working_directory

        self.potential_items = items or list()
        self.items = dict()  # filled in later by _get_items_to_analyze

        self.analyzers = analyzers or list()

        self.verbose = verbose

    def add_item(self, item):
        self.potential_items.append(item)

    # True/False, can this item be processed now?
    @staticmethod
    def can_analyze_item(item):
        """
        cannot analyze if the platform says the item is not ready
        """
        return item.status.name == EntityStatus.SUCCEEDED.name

    def _get_items_to_analyze(self):
        # returns a list of items derived from self.items that are available to analyze
        # ck4, review this behavior with the team/Benoit for interpretation re: current behavior

        # First sort items by whether they can currently be analyzed
        can_analyze = {}
        cannot_analyze = {}
        for item in self.potential_items:
            if self.can_analyze_item(item):
                can_analyze[item.uid] = item
            else:
                cannot_analyze[item.uid] = item

        # now consider item limiting arguments
        if self.partial_analyze_ok:
            if self.max_items_to_analyze is not None:
                to_analyze = {item.uid: item for item in list(can_analyze.values())[0:self.max_items_to_analyze]}
            else:
                to_analyze = can_analyze
        else:
            if len(cannot_analyze) > 0:
                raise self.ItemsNotReady('There are %d items that cannot be analyzed and partial_analyze_ok is off.' %
                                         len(cannot_analyze))
            to_analyze = can_analyze

        return to_analyze

    def add_analyzer(self, analyzer):
        self.analyzers.append(analyzer)

    # Ensure each analyzer has a unique uid in this context, updating them if needed
    def _update_analyzer_uids(self):
        unique_uids = {analyzer.uid for analyzer in self.analyzers}
        if len(unique_uids) < len(self.analyzers):
            for i in range(len(self.analyzers)):
                self.analyzers[i].uid += f'-{i}'

    # call from the beginning of self.analyze()
    def _initialize_analyzers(self):
        # Setup the working directory and call initialize() on each analyzer
        for analyzer in self.analyzers:
            if self.force_wd:
                analyzer.working_dir = self.working_dir
            else:
                analyzer.working_dir = analyzer.working_dir or self.working_dir

            analyzer.initialize()

            # make sure each analyzer in self.analyzers has a unique uid
            self._update_analyzer_uids()

    def _check_exception(self):
        exception = self.cache.get(EXCEPTION_KEY, default=None)
        if exception:
            print('\n' + exception)
            sys.stdout.flush()
            return True

    def _print_configuration(self, n_items, n_processes):
        n_ignored_items = len(self.potential_items) - n_items
        print('Analyze Manager')
        print(' | {} item(s) selected for analysis'.format(n_items))
        print(' | partial_analyze_ok is {}, max_items is {}, and {} item(s) are being ignored'
              .format(on_off(self.partial_analyze_ok), self.max_items_to_analyze, n_ignored_items))
        print(' | Analyzer(s): ')
        for analyzer in self.analyzers:
            print(' |  - {} File parsing: {} / Use cache: {})'
                  .format(analyzer.uid, on_off(analyzer.parse),
                          on_off(hasattr(analyzer, 'cache'))))
            if hasattr(analyzer, 'need_dir_map'):
                print(' | (Directory map: {}' % on_off(analyzer.need_dir_map))
        print(' | Pool of {} analyzing process(es)'.format(n_processes))

    # return T/F: did we succeed?
    def _run_and_wait_for_mapping(self, worker_pool, start_time):
        # add items to process (map)
        n_items = len(self.items)
        results = worker_pool.map_async(map_item, self.items.values())

        # Wait for the item map-results to be ready
        while not results.ready():
            # If an exception happen, kill everything and exit
            if self._check_exception():
                worker_pool.terminate()
                return False

            time_elapsed = time.time() - start_time
            if self.verbose:
                sys.stdout.write('\r {} Analyzing {}/{}... {} elapsed'
                                 .format(next(animation), len(self.cache), n_items, verbose_timedelta(time_elapsed)))
                sys.stdout.flush()

            if time_elapsed > ANALYZE_TIMEOUT:
                raise self.TimeOutException('Timeout while waiting the analysis to complete...')

            time.sleep(WAIT_TIME)

        # Verify that no simulation failed to process properly one last time.
        # ck4, should we error out if there is a failure rather than printing and continuing?? Ask Benoit.
        if self._check_exception():
            worker_pool.terminate()
            return False
        return True

    def _run_and_wait_for_reducing(self, worker_pool):
        # the keys in self.cache from select_simulation_data() calls are expected to be item ids. Each keyed value
        # contains analyzer_id: item_results_for_analyzer entries.
        finalize_results = {}
        for analyzer in self.analyzers:
            item_data_for_analyzer = {}
            for item_id in self.cache:
                # item = self.items[item_id]
                item_result = self.cache.get(item_id)
                item_data_for_analyzer[item_id] = item_result.get(analyzer.uid, None)  # item is currently unhashable if PythonSimulation, so temporarily using item_id, ck4
            finalize_results[analyzer.uid] = worker_pool.apply_async(analyzer.reduce, (item_data_for_analyzer,))

        # wait for results and clean up multiprocessing
        worker_pool.close()
        worker_pool.join()
        return finalize_results

    def analyze(self):
        start_time = time.time()

        # If no analyzers or simulations have been provided, there is nothing to do

        if len(self.analyzers) == 0:
            print('No analyzers were provided; cannot run analysis.')
            return False
        self._initialize_analyzers()

        if len(self.potential_items) == 0:
            print('No items were provided; cannot run analysis.')
            return False
        # trim processing to those items that are ready and match requested limits
        self.items = self._get_items_to_analyze()

        if len(self.items) == 0:
            print('No items are ready; cannot run analysis.')
            return False

        # initialize mapping results cache/storage
        n_items = len(self.items)
        n_processes = min(self.max_processes, max(n_items, 1))
        # self.initialize_cache(shards=n_processes, eviction_policy='none')  # ck4, restore if CacheEnabled is refactored

        # do any platform-specific initializations
        self.platform.initialize_for_analysis(self.items, self.analyzers)

        if self.verbose:
            self._print_configuration(n_items, n_processes)

        # Create the worker pool
        worker_pool = Pool(n_processes,
                           initializer=pool_worker_initializer,
                           initargs=(map_item, self.analyzers, self.cache, self.platform))

        success = self._run_and_wait_for_mapping(worker_pool=worker_pool, start_time=start_time)
        if not success:
            return success

        # At this point we have results for the individual items in self.cache.
        # Call the analyzer reduce methods

        finalize_results = self._run_and_wait_for_reducing(worker_pool=worker_pool)
        for analyzer in self.analyzers:
            analyzer.results = finalize_results[analyzer.uid].get()

        for analyzer in self.analyzers:
            analyzer.destroy()

        if self.verbose:
            total_time = time.time() - start_time
            time_str = verbose_timedelta(total_time)
            print('\r | Analysis complete. Took {} (~ {:.3f} per item)'.format(time_str, total_time / n_items))

        return True
