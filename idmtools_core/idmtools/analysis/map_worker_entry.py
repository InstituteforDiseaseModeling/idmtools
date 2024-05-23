"""
We define our map entry items here for analysis framework.

Most of these function are used either to initialize a thread or to handle exceptions while executing.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import itertools
from logging import getLogger, DEBUG
from idmtools.core.interfaces.ientity import IEntity
from idmtools.utils.file_parser import FileParser
from typing import TYPE_CHECKING, Dict
from idmtools.core.interfaces.iitem import IItem
from idmtools.entities.ianalyzer import TAnalyzerList

if TYPE_CHECKING:  # pragma: no cover
    from idmtools.entities.iplatform import IPlatform

logger = getLogger(__name__)


def map_item(item: IItem) -> Dict[str, Dict]:
    """
    Initialize some worker-global values; a worker process entry point for analyzer item-mapping.

    Args:
        item: The item (often simulation) to process.

    Returns:
        Dict[str, Dict]
    """
    # Retrieve the global variables coming from the pool initialization

    if logger.isEnabledFor(DEBUG):
        logger.debug(f"Init item {item.uid} in worker")
    analyzers = map_item.analyzers
    platform = map_item.platform

    if item.platform is None:
        item.platform = platform
    return _get_mapped_data_for_item(item, analyzers, platform)


def _get_mapped_data_for_item(item: IEntity, analyzers: TAnalyzerList, platform: 'IPlatform') -> Dict[str, Dict]:
    """
    Get mapped data from an item.

    Args:
        item: The :class:`~idmtools.entities.iitem.IItem` object to call analyzer
            :meth:`~idmtools.analysis.AddAnalyzer.map` methods on.
        analyzers: The :class:`~idmtools.analysis.IAnalyzer` items with
            :meth:`~idmtools.analysis.AddAnalyzer.map` methods to call on the provided items.
        platform: A platform object to query for information.

    Returns:
        Dict[str, Dict] - Array mapping file data to from str to contents

    """
    try:
        # determine which analyzers (and by extension, which filenames) are applicable to this item
        # ensure item has a platform
        item.platform = platform
        analyzers_to_use = [a for a in analyzers if a.filter(item)]
        analyzer_uids = [a.uid for a in analyzers]

        filenames = set(itertools.chain(*(a.filenames for a in analyzers_to_use)))
        filenames = [f.replace("\\", '/') for f in filenames]

        if logger.isEnabledFor(DEBUG):
            logger.debug(f"Analyzers to use on item: {str(analyzer_uids)}")
            logger.debug(f"Filenames to analyze: {filenames}")

        # The byte_arrays will associate filename with content
        if len(filenames) > 0:
            file_data = platform.get_files(item, filenames)
        else:
            file_data = dict()

        # Selected data will be a dict with analyzer.uid: data  entries
        selected_data = {}
        for analyzer in analyzers_to_use:
            # If the analyzer needs the parsed data, parse
            if analyzer.parse:
                logger.debug(f'Parsing content for {analyzer.uid}')
                data = {filename: FileParser.parse(filename, content) for filename, content in file_data.items() if filename in analyzer.filenames}
            else:
                # If the analyzer doesnt wish to parse, give the raw data
                data = {filename: content for filename, content in file_data.items() if filename in analyzer.filenames}

            # run the mapping routine for this analyzer and item
            logger.debug("Running map on selected data")
            selected_data[analyzer.uid] = analyzer.map(data, item)

        # Store all analyzer results for this item in the result cache
        if logger.isEnabledFor(DEBUG):
            logger.debug(f"Setting result to cache on {item.id}")
        logger.debug(f"Wrote Setting result to cache on {item.id}")
    except Exception as e:
        e.item = item
        logger.error(e)
        raise e
    return selected_data
