"""idmtools Analyzer manager.

AnalyzerManager is the "driver" of analysis. Analysis is mostly a map reduce operation.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from logging import getLogger, DEBUG
from typing import NoReturn, List, Dict, Tuple, Optional, TYPE_CHECKING
from tqdm import tqdm
from idmtools import IdmConfigParser
from idmtools.analysis.map_worker_entry import map_item
from idmtools.core import NoPlatformException
from idmtools.core.enums import ItemType
from idmtools.core.interfaces.ientity import IEntity
from idmtools.core.logging import VERBOSE, SUCCESS
from idmtools.entities.ianalyzer import IAnalyzer
from idmtools.utils.language import on_off, verbose_timedelta

if TYPE_CHECKING:  # pragma: no cover
    from idmtools.entities.iplatform import IPlatform

logger = getLogger(__name__)
user_logger = getLogger('user')


def pool_worker_initializer(func, analyzers, platform: 'IPlatform') -> NoReturn:
    """
    Initialize the pool worker, which allows the process pool to associate the analyzers, cache, and path mapping to the function executed to retrieve data.

    Using an initializer improves performance.

    Args:
        func: The function that the pool will call.
        analyzers: The list of all analyzers to run.
        platform: The platform to communicate with to retrieve files from.

    Returns:
        None
    """
    func.analyzers = analyzers
    func.platform = platform


class AnalyzeManager:
    """
    Analyzer Manager Class. This is the main driver of analysis.
    """
    ANALYZE_TIMEOUT = 3600 * 8  # Maximum seconds before timing out - set to 8 hours
    WAIT_TIME = 1.15  # How much time to wait between check if the analysis is done
    EXCEPTION_KEY = '__EXCEPTION__'

    class TimeOutException(Exception):
        """
        TimeOutException is raised when the analysis times out.
        """
        pass

    class ItemsNotReady(Exception):
        """
        ItemsNotReady is raised when items to be analyzed are still running.

        Notes:
            TODO - Add doc_link
        """
        pass

    def __init__(self, platform: 'IPlatform' = None, configuration: dict = None,
                 ids: List[Tuple[str, ItemType]] = None,
                 analyzers: List[IAnalyzer] = None, working_dir: str = None,
                 partial_analyze_ok: bool = False, max_items: Optional[int] = None, verbose: bool = True,
                 force_manager_working_directory: bool = False,
                 exclude_ids: List[str] = None, analyze_failed_items: bool = False,
                 max_workers: Optional[int] = None, executor_type: str = 'process'):
        """
        Initialize the AnalyzeManager.

        Args:
            platform (IPlatform): Platform
            configuration (dict, optional): Initial Configuration. Defaults to None.
            ids (Tuple[str, ItemType], optional): List of ids as pair of Tuple and ItemType. Defaults to None.
            analyzers (List[IAnalyzer], optional): List of Analyzers. Defaults to None.
            working_dir (str, optional): The working directory. Defaults to os.getcwd().
            partial_analyze_ok (bool, optional): Whether partial analysis is ok. When this is True, Experiments in progress or Failed can be analyzed. Defaults to False.
            max_items (int, optional): Max Items to analyze. Useful when developing and testing an Analyzer. Defaults to None.
            verbose (bool, optional): Print extra information about analysis. Defaults to True.
            force_manager_working_directory (bool, optional): [description]. Defaults to False.
            exclude_ids (List[str], optional): [description]. Defaults to None.
            analyze_failed_items (bool, optional): Allows analyzing of failed items. Useful when you are trying to aggregate items that have failed. Defaults to False.
            max_workers (int, optional): Set the max workers. If not provided, falls back to the configuration item *max_threads*. If max_workers is not set in configuration, defaults to CPU count
            executor_type: (str): Whether to use process or thread pooling. Process pooling is more efficient but threading might be required in some environments
        """
        super().__init__()
        if working_dir is None:
            working_dir = os.getcwd()
        if executor_type.lower() in ['process', 'thread']:
            self.executor_type = executor_type.lower()
        else:
            raise ValueError(f'{executor_type} is not a valid type for executor_type. Choose either "process" or "thread"')

        self.configuration = configuration or {}

        # load platform from context or from passed in value
        self.platform = platform
        self.__check_for_platform_from_context(platform)
        if max_workers is None:
            # check for max workers on platform, then in common
            if self.platform and hasattr(self.platform, '_config_block') and IdmConfigParser.get_option(self.platform._config_block, "max_workers", None):
                self.configuration['max_workers'] = int(IdmConfigParser.get_option(self.platform._config_block, "max_workers", None))
            elif IdmConfigParser().get_option('COMMON', 'max_workers', None):
                self.configuration['max_workers'] = int(IdmConfigParser().get_option('COMMON', 'max_workers'))

        # validate max_workers
        if max_workers is not None and max_workers < 1:
            raise ValueError("max_workers must be greater or equal to one")
        # ensure max workers is int
        self.max_processes = max_workers if max_workers is not None else self.configuration.get('max_workers', os.cpu_count())
        if logger.isEnabledFor(DEBUG):
            logger.debug(f'AnalyzeManager set to {self.max_processes}')

        # Should we continue analyzing even when we encounter an error?
        self.continue_on_error = False

        # should we attempt to analyze failed items
        self.analyze_failed_items = analyze_failed_items

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
        items: List[IEntity] = []
        for oid, otype in ids:
            logger.debug(f'Getting metadata for {oid} and {otype}')
            item = self.platform.get_item(oid, otype, force=True, raw=True)
            item.uid = str(item.id)
            item.platform = self.platform
            items.append(item)
        self.potential_items: List[IEntity] = []

        for i in items:
            logger.debug(f'Flattening items for {i.uid}')
            self.potential_items.extend(self.platform.flatten_item(item=i, raw=True))

        # These are leaf items to be ignored in analysis. Prune them from analysis.
        self.exclude_ids = exclude_ids or []
        for index, oid in enumerate(self.exclude_ids):
            self.exclude_ids[index] = str(oid)
        self.potential_items = [item for item in self.potential_items if item.uid not in self.exclude_ids]
        for item in self.potential_items:
            item.platform = self.platform

        logger.debug(f"Potential items to analyze: {len(self.potential_items)}")

        self._items = dict()  # filled in later by _get_items_to_analyze

        self.analyzers = analyzers or list()
        self.verbose = verbose

    def __check_for_platform_from_context(self, platform) -> 'IPlatform':  # noqa: F821
        """
        Try to determine platform of current object from self or current platform.

        Args:
            platform: Passed in platform object

        Raises:
            NoPlatformException: when no platform is on current context
        Returns:
            Platform object
        """
        if self.platform is None:
            # check context for current platform
            if platform is None:
                from idmtools.core.context import CURRENT_PLATFORM
                if CURRENT_PLATFORM is None:
                    raise NoPlatformException("No Platform defined on object, in current context, or passed to run")
                platform = CURRENT_PLATFORM
            self.platform = platform
        return self.platform

    def add_item(self, item: IEntity) -> NoReturn:
        """
        Add an additional item for analysis.

        Args:
            item: The new item to add for analysis.

        Returns:
            None
        """
        self.potential_items.extend(self.platform.flatten_item(item=item, raw=True))

    def _get_items_to_analyze(self) -> Dict[str, IEntity]:
        """
        Get a list of items derived from :meth:`self._items` that are available to analyze.

        Returns:
            A list of :class:`~idmtools.entities.iitem.IItem` objects.

        """
        # First sort items by whether they can currently be analyzed
        can_analyze = {}
        cannot_analyze = {}
        for item in self.potential_items:
            valid = self.platform.validate_item_for_analysis(item, self.analyze_failed_items)
            if valid:
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

    def add_analyzer(self, analyzer: IAnalyzer) -> NoReturn:
        """
        Add another analyzer to use on the items to be analyzed.

        Args:
            analyzer: An analyzer object (:class:`~idmtools.entities.ianalyzer.IAnalyzer`).

        Returns:
            None
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
                logger.debug(f'Analyzer {i.__class__} id set to {self.analyzers[i].uid}')

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
        user_logger.log(VERBOSE, 'Analyze Manager')
        user_logger.log(VERBOSE, f' | {n_items} item(s) selected for analysis')
        user_logger.log(VERBOSE, f' | partial_analyze_ok is {self.partial_analyze_ok}, max_items is '
                                 f'{self.max_items_to_analyze}, and {n_ignored_items} item(s) are being ignored')
        user_logger.log(VERBOSE, ' | Analyzer(s): ')
        for analyzer in self.analyzers:
            user_logger.log(VERBOSE, f' |  - {analyzer.uid} File parsing: {on_off(analyzer.parse)} / Use '
                                     f'cache: {on_off(hasattr(analyzer, "cache"))}')
            if hasattr(analyzer, 'need_dir_map'):
                user_logger.log(VERBOSE, f' | (Directory map: {on_off(analyzer.need_dir_map)}')
        user_logger.log(VERBOSE, f' | Pool of {n_processes} analyzing process(es)')

    def _run_and_wait_for_mapping(self, executor) -> Tuple[Dict, bool]:
        """
        Run and manage the mapping call on each item.

        Args:
            executor: A pool of workers.

        Returns:
            False if an exception occurred processing **.map** on any item; otherwise True (succeeded).

        """
        # add items to process (map)
        n_items = len(self._items)
        logger.debug(f"Number of items for analysis: {n_items}")
        logger.debug("Mapping the items for analysis")
        futures = dict()
        results = dict()
        status = True
        # create status bar and then queue our futures
        with tqdm(total=len(self._items)) as progress:
            for i in self._items.values():
                future = executor.submit(map_item, i)
                future.add_done_callback(lambda p: progress.update())
                futures[future] = i

            # wait on our futures to complete, catch exceptions, and aggregate results
            for future in as_completed(futures.keys()):
                if future.exception():
                    status = False
                    ex = future.exception()
                    user_logger.error(ex)
                    if not self.continue_on_error:
                        raise ex
                else:
                    results[futures[future]] = future.result()

        logger.debug(f"Result fetching status: : {status}")
        return results, status

    def _run_and_wait_for_reducing(self, executor, results) -> dict:
        """
        Run and manage the reduce call on the combined item results (by analyzer).

        Args:
            executor: A pool of workers.

        Returns:
            An analyzer ID keyed dictionary of finalize results.

        """
        # the keys in self.cache from map() calls are expected to be item ids. Each keyed value
        # contains analyzer_id: item_results_for_analyzer entries.
        logger.debug("Running reduce results")
        futures = {}
        finalize_results = {}
        # create a progress bar
        with tqdm(total=len(self.analyzers), desc="Running Analyzer Reduces") as progress:
            # for each analyzer, queue our futures
            for analyzer in self.analyzers:
                logger.debug(f"Gather data for {analyzer.uid}")
                item_data_for_analyzer = {}
                for item, data in results.items():
                    if analyzer.uid in data:
                        item_data_for_analyzer[item] = data[analyzer.uid]
                future = executor.submit(analyzer.reduce, item_data_for_analyzer)
                future.add_done_callback(lambda p: progress.update())

                logger.debug(f"Queueing {analyzer.uid}")
                futures[future] = analyzer.uid

            # wait on our futures, catch exceptions, and aggregate results
            logger.debug("Waiting for results")
            for future in as_completed(futures.keys()):
                if future.exception():
                    user_logger.error(f'Reduce for Analyzer {futures[future]} failed')
                    user_logger.exception(future.exception())
                    user_logger.error("See log for details")
                    if not self.continue_on_error:
                        sys.exit(-1)
                else:
                    finalize_results[futures[future]] = future.result()
            if logger.isEnabledFor(DEBUG):
                logger.debug("Finished reducing results")
            for future in futures.keys():
                future.cancel()
        return finalize_results

    def analyze(self) -> bool:
        """
        Process the provided items with the provided analyzers. This is the main driver method of :class:`AnalyzeManager`.

        Args:
            kwargs: extra parameters

        Returns:
            True on success; False on failure/exception.
        """
        start_time = time.time()

        # If no analyzers or simulations have been provided, there is nothing to do

        if len(self.analyzers) == 0:
            user_logger.error('No analyzers were provided; cannot run analysis.')
            return False
        self._initialize_analyzers()

        if len(self.potential_items) == 0:
            user_logger.error('No items were provided; cannot run analysis.')
            return False
        # trim processing to those items that are ready and match requested limits
        self._items: Dict[str, IEntity] = self._get_items_to_analyze()

        if len(self._items) == 0:
            user_logger.error('No items are ready; cannot run analysis.')
            return False

        # initialize mapping results cache/storage
        n_items = len(self._items)
        n_processes = min(self.max_processes, max(n_items, 1))

        logger.info(f'Analyzing {n_items}')

        # do any platform-specific initializations
        logger.debug("Triggering per group functions")
        for analyzer in self.analyzers:
            analyzer.per_group(items=self._items)

        if self.verbose:
            self._print_configuration(n_items, n_processes)

        no_print_config_exists = False
        # Before we initialize processes, ensure no warning about config are set
        if 'IDMTOOLS_NO_PRINT_CONFIG_USED' not in os.environ:
            os.environ['IDMTOOLS_NO_PRINT_CONFIG_USED'] = "1"
            os.environ['IDMTOOLS_HIDE_DEV_WARNING'] = "1"
            os.environ['IDMTOOLS_NO_CONFIG_WARNING'] = "1"
        else:
            no_print_config_exists = True

        # create worker pool
        try:
            # To ensure subprocesses reuse same config file, pass it through environment vars
            config_file = IdmConfigParser().get_config_path()
            if config_file:
                os.environ['IDMTOOLS_CONFIG_FILE'] = config_file

            # our options for our executor
            opts = dict(max_workers=n_processes, initializer=pool_worker_initializer, initargs=(map_item, self.analyzers, self.platform))
            # determine type. Most cases we want a process, but sometimes(like in Jupyter notebooks, we want to use threads)
            if self.executor_type == 'process':
                executor = ProcessPoolExecutor(**opts)
            else:
                executor = ThreadPoolExecutor(**opts)

            map_results, status = self._run_and_wait_for_mapping(executor)
            finalize_results = self._run_and_wait_for_reducing(executor, map_results)

        finally:
            # because of debug mode, we have to leave executor and let python handle the shutdown through del
            # see https://youtrack.jetbrains.com/issue/PY-34432
            os.environ['NO_LOGGING_INIT'] = 'n'
        logger.debug("Shutting down workers")

        for analyzer in self.analyzers:
            analyzer.results = finalize_results[analyzer.uid]

        logger.debug("Destroying analyzers")
        for analyzer in self.analyzers:
            analyzer.destroy()

        if not no_print_config_exists:
            del os.environ['IDMTOOLS_NO_PRINT_CONFIG_USED']
            del os.environ['IDMTOOLS_HIDE_DEV_WARNING']
            del os.environ['IDMTOOLS_NO_CONFIG_WARNING']
        if 'IDMTOOLS_CONFIG_FILE' in os.environ:
            del os.environ['IDMTOOLS_CONFIG_FILE']

        if self.verbose:
            total_time = time.time() - start_time
            time_str = verbose_timedelta(total_time)
            user_logger.log(SUCCESS, '\r | Analysis complete. Took {} '
                                     '(~ {:.3f} per item)'.format(time_str, total_time / n_items))
        return True
