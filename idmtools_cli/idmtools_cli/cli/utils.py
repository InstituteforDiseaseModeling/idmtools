import sys
import requests
from colorama import Fore

tags_help = "Tag to filter by. This should be in the form name value. For example, if you have a tag type=PythonTask " \
            "you would use --tags type PythonTask. In addition, you can provide multiple tags, ie --tags a 1 " \
            "--tags b 2. This will perform an AND based query on the tags meaning only jobs contains ALL the tags " \
            "specified will be displayed"


def show_error(message: requests.Response):
    """
    Display an error response from API on the command line

    Args:
        message (str): message to display

    Returns:

    """
    print(f'{Fore.RED}Error{Fore.RESET}: {message}')
    sys.exit(-1)
