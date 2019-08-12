import os
import sys
import time
import typing

from idmtools.analysis.map_worker_entry import map_item
from idmtools.core.CacheEnabled import CacheEnabled
from idmtools.core.enums import EntityStatus
from idmtools.utils.command_line import animation
from idmtools.utils.language import on_off, verbose_timedelta
from multiprocessing.pool import Pool
from typing import NoReturn

if typing.TYPE_CHECKING:
    from idmtools.core.types import TAnalyzer, TItem

ANALYZE_TIMEOUT = 3600 * 8  # Maximum seconds before timing out - set to 8 hours
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

    def add_item(self, item: 'TItem') -> NoReturn:
        """
        Add an additional item for analysis
        Args:
            item: the new thing to add for analysis

        Returns:

        """
        self.potential_items.append(item)

    @staticmethod
    def can_analyze_item(item: 'TItem') -> bool:
        """
        Can this item be processed now?
        Args:
            item: the thing to check for analyzability

        Returns: True/False

        """
        return item.status.name == EntityStatus.SUCCEEDED.name

    def _get_items_to_analyze(self) -> list:
        """
        Returns a list of items derived from self.items that are available to analyze
        Returns: a list of IItem objects

        """
        #
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

    def add_analyzer(self, analyzer: 'TAnalyzer') -> NoReturn:
        """
        Add another analyzer to use on the to-analyze items
        Args:
            analyzer: An analyzer object (IAnalyzer)

        Returns:

        """
        self.analyzers.append(analyzer)

    def _update_analyzer_uids(self) -> NoReturn:
        """
        Ensures that each analyzer has a unique uid in this context by updating them as needed
        Returns:

        """
        unique_uids = {analyzer.uid for analyzer in self.analyzers}
        if len(unique_uids) < len(self.analyzers):
            for i in range(len(self.analyzers)):
                self.analyzers[i].uid += f'-{i}'

    def _initialize_analyzers(self) -> NoReturn:
        """
        Do the steps needed to get the analyzers ready for item analysis
        Returns:

        """
        # Setup the working directory and call initialize() on each analyzer
        for analyzer in self.analyzers:
            if self.force_wd:
                analyzer.working_dir = self.working_dir
            else:
                analyzer.working_dir = analyzer.working_dir or self.working_dir

            analyzer.initialize()

            # make sure each analyzer in self.analyzers has a unique uid
            self._update_analyzer_uids()

    def _check_exception(self) -> bool:
        """
        Determines if an exception has occurred in the processing of items, printing any related information.
        Returns: True/False, has an exception occurred?

        """
        exception = self.cache.get(EXCEPTION_KEY, default=None)
        if exception:
            print('\n' + exception)
            sys.stdout.flush()
            ex = True
        else:
            ex = False
        return ex

    def _print_configuration(self, n_items: int, n_processes: int) -> NoReturn:
        """
        Display some information about an ongoing analysis
        Args:
            n_items: the number of items being analyzed
            n_processes: the number of active item processing handlers

        Returns:

        """
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

    def _run_and_wait_for_mapping(self, worker_pool: Pool, start_time: float) -> bool:
        """
        Runs and manages the mapping call on each item
        Args:
            worker_pool: a Pool of workers
            start_time: a relative time for updating the user on runtime

        Returns: False if an exception occurred processing .map on any item, otherwise True (succeeded)

        """
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

    def _run_and_wait_for_reducing(self, worker_pool: Pool) -> dict:
        """
        Runs and manages the reduce call on the combined item results (by analyzer)
        Args:
            worker_pool: a Pool of workers

        Returns: a analyzer-id keyed dict of finalize results

        """
        # the keys in self.cache from map() calls are expected to be item ids. Each keyed value
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

    def analyze(self) -> bool:
        """
        The main driver method of AnalyzerManager. Call this to process the provided items with the provided analyzers
        Returns: True on success, False on failure/exception

        """
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
