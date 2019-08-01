import itertools
import traceback

from idmtools_core.idmtools.analysis.file_parser import FileParser


def map_item(item) -> None:
    """
    A wrapper to bootstrap a process running the analyzer item-mapping driver with cross-process global values

    Args:
        item: The item (often simulation) to process

    Returns: Nothing
    """
    # Retrieve the global variables coming from the pool initialization
    analyzers = map_item.analyzers
    cache = map_item.cache
    platform = map_item.platform

    get_mapped_data_for_item(item, analyzers, cache, platform)


def get_mapped_data_for_item(item, analyzers, cache, platform):
    # determine which analyzers (and by extension, which filenames) are applicable to this item

    try:
        analyzers_to_use = [a for a in analyzers if a.filter(item)]
    except Exception:
        analyzer_uids = [a.uid for a in analyzers]
        set_exception(step="Item filtering",
                      info={"Item": item, "Analyzers": ", ".join(analyzer_uids)},
                      cache=cache)

    filenames = set(itertools.chain(*(a.filenames for a in analyzers_to_use)))

    # The byte_arrays will associate filename with content
    try:
        file_data = platform.get_files(item, filenames)  # make sure this does NOT error when filenames is empty
    except Exception:
        # an error has occurred
        analyzer_uids = [a.uid for a in analyzers]
        set_exception(step="data retrieval",
                      info={"Item": item, "Analyzers": ", ".join(analyzer_uids), "Files": ", ".join(filenames)},
                      cache=cache)
        return False

    # Selected data will be a dict with analyzer.uid: data  entries
    selected_data = {}
    for analyzer in analyzers_to_use:
        # If the analyzer needs the parsed data, parse
        if analyzer.parse:
            try:
                data = {filename: FileParser.parse(filename, content)
                        for filename, content in file_data.items()}
            except Exception:
                set_exception(step="data parsing",
                              info={"Item": item, "Analyzer": analyzer.uid},
                              cache=cache)
                return False
        else:
            # If the analyzer doesnt wish to parse, give the raw data
            data = file_data

        # run the mapping routine for this analyzer and item
        try:
            selected_data[analyzer.uid] = analyzer.map(data, item)
        except Exception:
            set_exception(step="data processing", info={"Item": item, "Analyzer": analyzer.uid},
                          cache=cache)
            return False

    # Store all analyzer results for this item in the result cache
    cache.set(item.uid, selected_data)
    return True


def set_exception(step: str, info: dict, cache: any) -> None:
    """
    Helper to quickly set an exception in the cache.

    Args:
        step: Which step encountered an error
        info: Dictionary for additional information to add to the message
        cache: The cache object in which to set the exception

    Returns: Nothing

    """
    from idmtools_core.idmtools.analysis.AnalyzeManager import EXCEPTION_KEY

    # construct exception message including traceback
    message = f'\nAn exception has been raised during {step}.\n'
    for key, value in info.items():
        message += f'- {key}: {value}\n'
    message += f'\n{traceback.format_exc()}\n'

    cache.set(EXCEPTION_KEY, message)
