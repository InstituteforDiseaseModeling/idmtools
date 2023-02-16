"""
Utils for platform operations.

Here we have mostly utilities to handle batch operations which tend to overlap across different item types.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from concurrent.futures import as_completed, Future
from concurrent.futures.process import ProcessPoolExecutor
from concurrent.futures.thread import ThreadPoolExecutor
from functools import partial
from logging import getLogger, DEBUG
from os import cpu_count
from typing import List, Union, Generator, Iterable, Callable, Any
from more_itertools import chunked
from idmtools.core import EntityContainer
from idmtools.entities.templated_simulation import TemplatedSimulations

logger = getLogger(__name__)
user_logger = getLogger('user')
# Global executor
EXECUTOR = None


def batch_items(items: Union[Iterable, Generator], batch_size=16):
    """
    Batch items.

    Args:
        items: Items to batch
        batch_size: Size of the batch

    Returns:
        Generator

    Raises:
        StopIteration
    """
    for item_chunk in chunked(items, batch_size):
        logger.info('created chunk')
        yield item_chunk
    raise StopIteration


def item_batch_worker_thread(create_func: Callable, items: Union[List], **kwargs) -> List:
    """
    Default batch worker thread function. It just calls create on each item.

    Args:
        create_func: Create function for item
        items: Items to create

    Returns:
        List of items created
    """
    if logger.isEnabledFor(DEBUG):
        logger.debug(f'Create {len(items)}')

    ret = []
    for item in items:
        ret.append(create_func(item, **kwargs))

    return ret


def batch_create_items(items: Union[Iterable, Generator], batch_worker_thread_func: Callable[[List], List] = None,
                       create_func: Callable[..., Any] = None, display_progress: bool = True,
                       progress_description: str = "Commissioning items", unit: str = None, **kwargs):
    """
    Batch create items. You must specify either batch_worker_thread_func or create_func.

    Args:
        items: Items to create
        batch_worker_thread_func: Optional Function to execute. Should take a list and return a list
        create_func: Optional Create function
        display_progress: Enable progress bar
        progress_description: Description to show in progress bar
        unit: Unit for progress bar
        **kwargs:

    Returns:
        Batches crated results
    """
    global EXECUTOR
    from idmtools.config import IdmConfigParser
    from idmtools.utils.collections import ExperimentParentIterator

    max_workers = kwargs.get('max_workers', None)

    # Consider values from the block that Platform uses
    _batch_size = int(IdmConfigParser.get_option(None, "batch_size", fallback=16))

    batch_size = kwargs.get('batch_size', None)
    if batch_size is not None:
        _batch_size = batch_size

    if display_progress and not IdmConfigParser.is_progress_bar_disabled():
        from tqdm import tqdm
        extra_args = dict(unit=unit) if unit else dict()
        prog = tqdm(desc="Initializing objects for creation", **extra_args)
    else:
        prog = None

    if EXECUTOR is None:
        _workers_per_cpu = IdmConfigParser.get_option(None, "workers_per_cpu", fallback=None)
        if _workers_per_cpu:
            _max_workers = int(_workers_per_cpu) * cpu_count()
            if logger.isEnabledFor(DEBUG):
                logger.debug(f"workers set by cpu: {_workers_per_cpu} * {cpu_count()}")
        else:
            _max_workers = int(IdmConfigParser.get_option(None, "max_workers", fallback=16))

        if max_workers is not None:
            _max_workers = max_workers

        logger.info(f'Creating {_max_workers} Platform Workers')
        default_pool_executor = IdmConfigParser.get_option(None, "default_pool_executor", fallback="thread").lower()
        if default_pool_executor == "process":
            EXECUTOR = ProcessPoolExecutor(max_workers=_max_workers)
        else:
            EXECUTOR = ThreadPoolExecutor(max_workers=_max_workers)

    if batch_worker_thread_func is None:

        if create_func is None:
            raise ValueError("You must provide either an item create callback or a item batch worker thread callback to"
                             " perform batches")
        batch_worker_thread_func = partial(item_batch_worker_thread, create_func, **kwargs)
    if logger.isEnabledFor(DEBUG):
        logger.debug(f'Batching creation by {_batch_size}')

    futures = []

    total = 0
    parent = None
    if isinstance(items, ExperimentParentIterator) and isinstance(items.items, TemplatedSimulations):
        parent = items.parent
        i = items.items.simulations().generator
    elif isinstance(items, ExperimentParentIterator) and isinstance(items.items, EntityContainer):
        parent = items.parent
        i = items.items
    else:
        i = items
    if display_progress and not IdmConfigParser.is_progress_bar_disabled() and hasattr(items, '__len__'):
        prog.total = len(items)
    for chunk in chunked(i, _batch_size):
        total += len(chunk)
        if parent:
            for c in chunk:
                c.parent = parent
        if logger.isEnabledFor(DEBUG):
            logger.debug(f"Submitting chunk: {len(chunk)}")
        if display_progress and not IdmConfigParser.is_progress_bar_disabled():
            prog.update(len(chunk))
        futures.append(EXECUTOR.submit(batch_worker_thread_func, chunk))

    results = []
    if display_progress and not IdmConfigParser.is_progress_bar_disabled():
        prog.set_description(progress_description)
        prog.reset(total)
        results = show_progress_of_batch(prog, futures)
    else:
        for future in futures:
            results.extend(future.result())

    return results


def show_progress_of_batch(progress_bar: 'tqdm', futures: List[Future]) -> List:  # noqa: F821
    """
    Show progress bar for batch.

    Args:
        progress_bar: Progress bar
        futures: List of futures that are still running/queued

    Returns:
        Returns results
    """
    results = []
    for future in as_completed(futures):
        result = future.result()
        progress_bar.update(len(result))
        results.extend(future.result())
    return results
