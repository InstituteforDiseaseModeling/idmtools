from math import floor
from typing import Dict
from colorama import Fore, Back
from idmtools_platform_local.config import DATA_PATH
from idmtools_platform_local.status import Status

status_text_color_map = dict(failed=Fore.RED, in_progress=Fore.YELLOW, done=Fore.GREEN, canceled=Fore.CYAN)
status_progress_color_map = dict(failed=Back.RED, in_progress=Back.YELLOW, done=Back.GREEN, canceled=Fore.CYAN)

tags_help = "Tag to filter by. This should be in the form name value. For example, if you have a tag type=PythonTask " \
            "you would use --tags type PythonTask. In addition, you can provide multiple tags, ie --tags a 1 " \
            "--tags b 2. This will perform an AND based query on the tags meaning only jobs caontain ALL the tags " \
            "specified will be displayed"


def colorize_status(status: Status) -> str:
    """
    Colorizes a status for the console
    Args:
        status (Status): Status to colorize

    Returns:
        str: Unicode colorized string of the status
    """
    if str(status) in status_text_color_map:
        status = status_text_color_map[str(status)] + str(status) + Fore.WHITE
    else:
        status = str(status)
    return status


def parent_status_to_progress(status: Dict[Status, int], width: int = 12) -> str:
    """
    Convert a status object into a colorized progress bar for the console

    Args:
        status (Dict[Status, int]): Status dictionary. The dictionary should Status values for keys and the values should be the total
            number of simulations in the specific status. An example would be {Status.done: 30, Status.created: 1}
        width (int): The desired width of the progress bar

    Returns:
        str: Progress bar of the status
    """
    status = {str(k): v for k, v in status.items()}
    total = sum([v for k, v in status.items()])

    result = ''
    used = 0
    total_complete_or_failed = sum([v for k, v in status.items() if k in ['failed', 'done']])

    status_order = ['done', 'in_progress', 'failed']
    for label in status_order:
        if label in status:
            w = floor(status[label] / total * width)
            if w > 0:
                color = status_progress_color_map[label]
                result += color + (' ' * w)
                used += w

    # add the remaining in progress
    if width - used > 0:
        result += Back.WHITE + (' ' * (width - used))

    result += Back.RESET
    result = '[' + result + ']' + '{0}/{1} ({2:.1f}%)'.format(total_complete_or_failed, total,
                                                              total_complete_or_failed / total * 100.0)
    return result


def urlize_data_path(path: str) -> str:
    """
    URL-ize a data-path so it can be made click-able in the console(if the console supports it)
    Args:
        path (str): path to urilze
    Returns:
        str: Path as URL.
    """
    return path.replace(DATA_PATH, 'http://localhost:5000/data')
