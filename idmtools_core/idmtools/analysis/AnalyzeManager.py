import os
import sys
import time
import typing
from logging import getLogger, DEBUG

from idmtools.analysis.map_worker_entry import map_item
from idmtools.core import CacheEnabled
from idmtools.utils.command_line import animation
from idmtools.utils.language import on_off, verbose_timedelta
from multiprocessing.pool import Pool
from typing import NoReturn

if typing.TYPE_CHECKING:
    from idmtools.entities.ianalyzer import TAnalyzer
    from idmtools.core.interfaces.iitem import TItem, TItemList

logger = getLogger(__name__)


def pool_worker_initializer(func, analyzers, cache, platform) -> None:
    """
    Initialize the pool worker, which allows the process pool to associate the analyzers, cache, 
    and path mapping to the function executed to retrieve data. Using an initializer improves performance.

    Args:
        func: The function that the pool will call.
        analyzers: The list of all analyzers to run.
        cache: The cache object.
        platform: The platform to communicate with to retrieve files from.

    Returns:
        None
    """
    func.analyzers = analyzers
    func.cache = cache
    func.platform = platform


class AnalyzeManager(CacheEnabled):
    ANALYZE_TIMEOUT = 3600 * 8  # Maximum seconds before timing out - set to 8 hours
    WAIT_TIME = 1.15  # How much time to wait between check if the analysis is done
    EXCEPTION_KEY = '__EXCEPTION__'

    class TimeOutException(Exception):
        pass

    class ItemsNotReady(Exception):
        pass

    def __init__(self, platform, configuration=None, ids=None, analyzers=None, working_dir=os.getcwd(),
                 partial_analyze_ok=False, max_items=None, verbose=True, force_manager_working_directory=False):
        super().__init__()
        self.configuration = configuration or {}
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

        # Take the provided ids and determine the full set of unique root items (e.g. simulations) in them to analyze
        logger.debug("Load information about items from platform")
        ids = list(set(ids or list()))  # uniquify
        items = [platform.get_item(oid, otype, force=True) for oid, otype in ids]
        self.potential_items = []

        for i in items:
            self.potential_items.extend(platform.flatten_item(item=i))
        logger.debug(f"Potential items to analyze: {len(self.potential_items)}")
        self._items = dict()  # filled in later by _get_items_to_analyze

        self.analyzers = analyzers or list()
        self.verbose = verbose

    def add_item(self, item: 'TEntity') -> NoReturn:
        """
        Add an additional item for analysis.

        Args:
            item: The new item to add for analysis.

        Returns:
            None
        """

        self.potential_items.extend(self.platform.flatten_item(item=item))

    def _get_items_to_analyze(self) -> 'dict':
        """
        Get a list of items derived from :meth:`self._items` that are available to analyze.
        
        Returns: 
            A list of :class:`~idmtools.entities.iitem.IItem` objects.

        """
        #
        # ck4, review this behavior with the team/Benoit for interpretation re: current behavior

        # First sort items by whether they can currently be analyzed
        can_analyze = {}
        cannot_analyze = {}
        for item in self.potential_items:
            if item.succeeded:
                can_analyze[item.uid] = item
            else:
                cannot_analyze[item.uid] = item

        # now consider item limiting arguments
        if self.partial_analyze_ok:
            if self.max_items_to_analyze is not None:
                return {item.uid: item for item in list(can_analyze.values())[0:self.max_items_to_analyze]}
            return can_analyze

        if len(cannot_analyze) > 0:
            raise self.ItemsNotReady('There are %d items that cannot be analyzed and partial_analyze_ok is off.' %
                                     len(cannot_analyze))

        return can_analyze

    def add_analyzer(self, analyzer: 'TAnalyzer') -> NoReturn:
        """
        Add another analyzer to use on the items to be analyzed.

        Args:
            analyzer: An analyzer object (:class:`~idmtools.entities.ianalyzer.IAnalyzer`).

        Returns:

        """
        self.analyzers.append(analyzer)

    def _update_analyzer_uids(self) -> NoReturn:
        """
        Ensure that each analyzer has a unique ID in this context by updating them as needed.

        Returns:
            None
        """
        unique_uids = {analyzer.uid for analyzer in self.analyzers}
        if len(unique_uids) < len(self.analyzers):
            for i in range(len(self.analyzers)):
                self.analyzers[i].uid += f'-{i}'

    def _initialize_analyzers(self) -> NoReturn:
        """
        Do the steps needed to prepare analyzers for item analysis.

        Returns:
            None
        """
        logger.debug("Initializing Analyzers")
        # Setup the working directory and call initialize() on each analyzer
        for analyzer in self.analyzers:
            if self.force_wd:
                analyzer.working_dir = self.working_dir
            else:
                analyzer.working_dir = analyzer.working_dir or self.working_dir

            if logger.isEnabledFor(DEBUG):
                logger.debug(f"Analyzer working directory set to {analyzer.working_dir}")
            analyzer.initialize()

        # make sure each analyzer in self.analyzers has a unique uid
        self._update_analyzer_uids()

    def _check_exception(self) -> bool:
        """
        Determines if an exception has occurred in the processing of items, printing any related information.

        Returns: 
            A Boolean indicating if an exception has occurred. 

        """
        exception = self.cache.get(self.EXCEPTION_KEY, default=None)
        if exception:
            if logger.isEnabledFor(DEBUG):
                logger.debug(exception)
            print('\n' + exception)
            sys.stdout.flush()
            ex = True
        else:
            ex = False
        return ex

    def _print_configuration(self, n_items: int, n_processes: int) -> NoReturn:
        """
        Display some information about an ongoing analysis.

        Args:
            n_items: The number of items being analyzed.
            n_processes: The number of active item processing handlers.

        Returns:
            None
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
        Run and manage the mapping call on each item.

        Args:
            worker_pool: A pool of workers.
            start_time: A relative time for updating the user on runtime.

        Returns: 
            False if an exception occurred processing **.map** on any item; otherwise True (succeeded).

        """
        # add items to process (map)
        n_items = len(self._items)
        logger.debug(f"Number of items for analysis: {n_items}")
        logger.debug("Mapping the items for analysis")
        results = worker_pool.map_async(map_item, self._items.values())

        # Wait for the item map-results to be ready
        while not results.ready():
            # If an exception happen, kill everything and exit
            if self._check_exception():
                logger.debug("Terminating workerpool")
                worker_pool.terminate()
                return False

            time_elapsed = time.time() - start_time
            if self.verbose:
                sys.stdout.write('\r {} Analyzing {}/{}... {} elapsed'
                                 .format(next(animation), len(self.cache), n_items, verbose_timedelta(time_elapsed)))
                sys.stdout.flush()

            if time_elapsed > self.ANALYZE_TIMEOUT:
                raise self.TimeOutException('Timeout while waiting the analysis to complete...')

            time.sleep(self.WAIT_TIME)

        # Verify that no simulation failed to process properly one last time.
        # ck4, should we error out if there is a failure rather than printing and continuing?? Ask Benoit.
        if self._check_exception():
            logger.debug("Terminating workerpool")
            worker_pool.terminate()
            return False
        return True

    def _run_and_wait_for_reducing(self, worker_pool: Pool) -> dict:
        """
        Run and manage the reduce call on the combined item results (by analyzer).

        Args:
            worker_pool: A pool of workers.

        Returns: 
            An analyzer ID keyed dictionary of finalize results.

        """
        # the keys in self.cache from map() calls are expected to be item ids. Each keyed value
        # contains analyzer_id: item_results_for_analyzer entries.
        logger.debug("Finalizing results")
        finalize_results = {}
        for analyzer in self.analyzers:
            item_data_for_analyzer = {}
            for item_id in self.cache:
                item = self._items[item_id]
                item_result = self.cache.get(item_id)
                item_data_for_analyzer[item] = item_result.get(analyzer.uid, None)
            finalize_results[analyzer.uid] = worker_pool.apply_async(analyzer.reduce, (item_data_for_analyzer,))

        # wait for results and clean up multiprocessing
        worker_pool.close()
        worker_pool.join()
        if logger.isEnabledFor(DEBUG):
            logger.debug("Finished finalizing results")
        return finalize_results

    def analyze(self) -> bool:
        """
        Process the provided items with the provided analyzers. This is the main driver method of 
        :class:`AnalyzeManager`. 

        Returns: 
            True on success; False on failure/exception.

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
        self._items = self._get_items_to_analyze()

        if len(self._items) == 0:
            print('No items are ready; cannot run analysis.')
            return False

        # initialize mapping results cache/storage
        n_items = len(self._items)
        n_processes = min(self.max_processes, max(n_items, 1))

        # Initialize the cache
        logger.debug("Initializing Analysis Cache")
        self.initialize_cache(shards=n_processes, eviction_policy='none')

        # do any platform-specific initializations
        logger.debug("Triggering per group functions")
        for analyzer in self.analyzers:
            analyzer.per_group(items=self._items)

        if self.verbose:
            self._print_configuration(n_items, n_processes)

        # Create the worker pool
        worker_pool = Pool(n_processes,
                           initializer=pool_worker_initializer,
                           initargs=(map_item, self.analyzers, self.cache, self.platform))

        success = self._run_and_wait_for_mapping(worker_pool=worker_pool, start_time=start_time)
        logger.debug(f"Success: {success}")
        if not success:
            return success

        # At this point we have results for the individual items in self.cache.
        # Call the analyzer reduce methods

        finalize_results = self._run_and_wait_for_reducing(worker_pool=worker_pool)
        for analyzer in self.analyzers:
            analyzer.results = finalize_results[analyzer.uid].get()

        logger.debug(str(analyzer.results))

        logger.debug("Destroying analyzers")
        for analyzer in self.analyzers:
            analyzer.destroy()

        if self.verbose:
            total_time = time.time() - start_time
            time_str = verbose_timedelta(total_time)
            print('\r | Analysis complete. Took {} (~ {:.3f} per item)'.format(time_str, total_time / n_items))

        return True
