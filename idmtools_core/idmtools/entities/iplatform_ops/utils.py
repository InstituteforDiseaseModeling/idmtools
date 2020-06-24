from concurrent.futures.thread import ThreadPoolExecutor
from concurrent.futures import as_completed, Future
from functools import partial
from logging import getLogger, DEBUG
from typing import List, Union, Generator, Iterable, Callable, Any
from more_itertools import chunked
from tqdm import tqdm
from idmtools.core import EntityContainer
from idmtools.entities.templated_simulation import TemplatedSimulations

logger = getLogger(__name__)
user_logger = getLogger('user')
# Global executor
EXECUTOR = None


def batch_items(items: Union[Iterable, Generator], batch_size=16):
    """
    Batch items

    Args:
        items:
        batch_size:

    Returns:

    """
    for item_chunk in chunked(items, batch_size):
        logger.info('created chunk')
        yield item_chunk
    raise StopIteration


def item_batch_worker_thread(create_func: Callable, items: Union[List]) -> List:
    """
    Default batch worker thread function. It just calls create on each item

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
        ret.append(create_func(item))

    return ret


def batch_create_items(items: Union[Iterable, Generator], batch_worker_thread_func: Callable[[List], List] = None,
                       create_func: Callable[..., Any] = None, display_progress: bool = True,
                       progress_description: str = "Commissioning items", **kwargs):
    """
    Batch create items. You must specify either batch_worker_thread_func or create_func

    Args:
        items: Items to create
        batch_worker_thread_func: Optional Function to execute. Should take a list and return a list
        create_func: Optional Create function
        display_progress: Enable progress bar
        progress_description: Description to show in progress bar
        **kwargs:

    Returns:

    """
    global EXECUTOR
    from idmtools.config import IdmConfigParser
    from idmtools.utils.collections import ParentIterator

    # Consider values from the block that Platform uses
    _batch_size = int(IdmConfigParser.get_option(None, "batch_size", fallback=16))

    if EXECUTOR is None:
        _max_workers = int(IdmConfigParser.get_option(None, "max_workers", fallback=16))
        logger.info(f'Creating {_max_workers} Platform Workers')
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
    if isinstance(items, ParentIterator) and isinstance(items.items, TemplatedSimulations):
        parent = items.parent
        i = items.items.simulations().generator
    elif isinstance(items, ParentIterator) and isinstance(items.items, EntityContainer):
        parent = items.parent
        i = items.items
    else:
        i = items
    for chunk in chunked(i, _batch_size):
        total += len(chunk)
        if parent:
            for c in chunk:
                c.parent = parent
        futures.append(EXECUTOR.submit(batch_worker_thread_func, chunk))

    results = []
    if display_progress:
        results = show_progress_of_batch(futures, progress_description, total)
    else:
        for future in futures:
            results.extend(future.result())

    return results


def show_progress_of_batch(futures: List[Future], progress_description: str, total: int) -> List:
    """
    Show progress bar for batch

    Args:
        futures: List of futures that are still running/queued
        progress_description: Progress description
        total: Total items being loaded(since we are loading in batches)

    Returns:

    """
    results = []
    with tqdm(futures, desc=progress_description, total=total) as prog:
        for future in as_completed(futures):
            result = future.result()
            prog.update(len(result))
            results.extend(future.result())
    return results
