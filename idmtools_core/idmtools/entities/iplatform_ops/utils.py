from functools import partial
from logging import getLogger, DEBUG
from typing import List, Union, Generator, Iterable, Callable, Sized

from more_itertools import grouper

logger = getLogger(__name__)


def batch_items(items: Union[Iterable, Generator], batch_size=16) -> Generator[List, None, None]:
    for groups in grouper(items, batch_size):
        sims = []
        for sim in filter(None, groups):
            sims.append(sim)
        yield sims


def item_batch_worker_thread(create_func: Callable, items: Union[List]):
    if logger.isEnabledFor(DEBUG):
        logger.debug(f'Create {len(items)}')

    ids = []
    for item in items:
        ids = create_func(item)

    for uid, item in zip(ids, items):
        item.uid = uid
    return items


def batch_create_items(items: Union[Iterable, Generator], create_func: Callable, **kwargs):
    """
    Create all the simulations contained in the experiment on the platform.
    """
    from idmtools.config import IdmConfigParser
    from concurrent.futures.thread import ThreadPoolExecutor
    from idmtools.core import EntityContainer

    # Consider values from the block that Platform uses
    _max_workers = IdmConfigParser.get_option(None, "max_workers")
    _batch_size = IdmConfigParser.get_option(None, "batch_size")

    _max_workers = int(_max_workers) if _max_workers else 16
    _batch_size = int(_batch_size) if _batch_size else 16

    logger.debug(f'Creating Batch of items with {_max_workers} and a {_batch_size}')

    with ThreadPoolExecutor(max_workers=16) as executor:
        platform_partial = partial(item_batch_worker_thread, create_func, **kwargs)
        results = executor.map(platform_partial,  batch_items(items, batch_size=_batch_size))

    results = EntityContainer()
    for item_batch in results:
        for item in item_batch:
            results.append(item)

    return results
