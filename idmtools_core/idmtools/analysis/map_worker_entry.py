import itertools
import time
import traceback
import typing
from logging import getLogger, DEBUG

from idmtools.utils.file_parser import FileParser
from typing import NoReturn

if typing.TYPE_CHECKING:
    from idmtools.entities.iplatform import TPlatform
    from idmtools.core.interfaces.iitem import TItem
    from idmtools.entities.ianalyzer import TAnalyzerList
    from diskcache import Cache

logger = getLogger(__name__)


def map_item(item: 'TItem') -> NoReturn:
    """
    Initialize some worker-global values; a worker process entry point for analyzer item-mapping.

    Args:
        item: The item (often simulation) to process.

    Returns:
        None
    """
    # Retrieve the global variables coming from the pool initialization
    analyzers = map_item.analyzers
    cache = map_item.cache
    platform = map_item.platform

    _get_mapped_data_for_item(item, analyzers, cache, platform)


def _get_mapped_data_for_item(item: 'TItem', analyzers: 'TAnalyzerList', cache: 'Cache', platform: 'TPlatform') -> bool:
    """

    Args:
        item: The :class:`~idmtools.entities.iitem.IItem` object to call analyzer 
            :meth:`~idmtools.analysis.AddAnalyzer.map` methods on.
        analyzers: The :class:`~idmtools.analysis.IAnalyzer` items with 
            :meth:`~idmtools.analysis.AddAnalyzer.map` methods to call on the provided items.
        cache: The disk cache object to store item :meth:`~idmtools.analysis.AddAnalyzer.map` 
            results in.
        platform: A platform object to query for information.

    Returns: 
        False if an exception occurred; else True (succeeded).

    """
    # determine which analyzers (and by extension, which filenames) are applicable to this item
    try:
        analyzers_to_use = [a for a in analyzers if a.filter(item)]
        analyzer_uids = [a.uid for a in analyzers]
    except Exception:
        analyzer_uids = [a.uid for a in analyzers]
        _set_exception(step="Item filtering",
                       info={"Item": item, "Analyzers": ", ".join(analyzer_uids)},
                       cache=cache)

    filenames = set(itertools.chain(*(a.filenames for a in analyzers_to_use)))

    if logger.isEnabledFor(DEBUG):
        logger.debug(f"Analyzers to use on item: {str(analyzer_uids)}")
        logger.debug(f"Filenames to analyze: {filenames}")

    # The byte_arrays will associate filename with content
    try:
        file_data = platform.get_files(item, filenames)  # make sure this does NOT error when filenames is empty
    except Exception:
        # an error has occurred
        analyzer_uids = [a.uid for a in analyzers]
        _set_exception(step="data retrieval",
                       info={"Item": item, "Analyzers": ", ".join(analyzer_uids), "Files": ", ".join(filenames)},
                       cache=cache)
        return False

    # Selected data will be a dict with analyzer.uid: data  entries
    selected_data = {}
    for analyzer in analyzers_to_use:
        # If the analyzer needs the parsed data, parse
        if analyzer.parse:
            logger.debug(f'Parsing content for {analyzer.uid}')
            try:
                data = {filename: FileParser.parse(filename, content)
                        for filename, content in file_data.items()}
            except Exception:
                _set_exception(step="data parsing",
                               info={"Item": item, "Analyzer": analyzer.uid},
                               cache=cache)
                return False
        else:
            # If the analyzer doesnt wish to parse, give the raw data
            data = file_data

        # run the mapping routine for this analyzer and item
        try:
            logger.debug("Running map on selected data")
            selected_data[analyzer.uid] = analyzer.map(data, item)
        except Exception:
            _set_exception(step="data processing", info={"Item": item, "Analyzer": analyzer.uid},
                           cache=cache)
            return False

    # Store all analyzer results for this item in the result cache
    if logger.isEnabledFor(DEBUG):
        logger.debug(f"Setting result to cache on {item.uid}")
    done = False
    retries=0
    while not done and retries < 6:
        try:
            cache.set(item.uid, selected_data)
            done = True
        except TimeoutError as e:
            retries+=1
            pass
        if retries > 5:
            raise StopAsyncIteration("Error set value to cache")
    logger.debug(f"Wrote Setting result to cache on {item.uid}")
    return True


def _set_exception(step: str, info: dict, cache: 'Cache') -> NoReturn:
    """
    Set an exception in the cache in a standardized way.

    Args:
        step: The step that encountered an error.
        info: A dictionary for additional information to add to the message.
        cache: The cache object in which to set the exception.

    Returns:

    """
    from idmtools_core.idmtools.analysis.AnalyzeManager import AnalyzeManager

    # construct exception message including traceback
    message = f'\nAn exception has been raised during {step}.\n'
    for key, value in info.items():
        message += f'- {key}: {value}\n'
    message += f'\n{traceback.format_exc()}\n'

    cache.set(AnalyzeManager.EXCEPTION_KEY, message)
