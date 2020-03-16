from concurrent.futures.thread import ThreadPoolExecutor
from functools import partial
from logging import getLogger, DEBUG
from typing import List, Union, Generator, Iterable, Callable, Any

from more_itertools import chunked
from tqdm import tqdm

from idmtools.entities.templated_simulation import TemplatedSimulations

logger = getLogger(__name__)
# Global executor
EXECUTOR = None


def batch_items(items: Union[Iterable, Generator], batch_size=16):
    for item_chunk in chunked(items, batch_size):
        print('created chunk')
        yield item_chunk
    raise StopIteration


def item_batch_worker_thread(create_func: Callable, items: Union[List]):
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
    Create all the simulations contained in the experiment on the platform.
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

    chunk = []
    futures = []

    total = 0
    parent = None
    if isinstance(items, ParentIterator) and isinstance(items.items, TemplatedSimulations):
        parent = items.parent
        items = items.items.simulations().generator
    for chunk in chunked(items, _batch_size):
        total += len(chunk)
        if parent:
            for c in chunk:
                c.parent = parent
        futures.append(EXECUTOR.submit(batch_worker_thread_func, chunk))
    # for item in items:
    #     chunk.append(item)
    #     if len(chunk) >= _batch_size:
    #         futures.append(EXECUTOR.submit(batch_worker_thread_func, chunk))
    #         chunk = []
    # if len(chunk):
    #    futures.append(EXECUTOR.submit(batch_worker_thread_func, chunk))

    results = []
    prog = tqdm(futures, desc=progress_description) if display_progress else futures
    for future in prog:
        results.extend(future.result())

    return results
