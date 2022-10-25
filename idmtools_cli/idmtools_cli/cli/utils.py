"""Defines utilities used with the cli commands."""
import sys
from typing import NoReturn, Union
import requests
from click import UsageError
from colorama import Fore
from idmtools.core.platform_factory import Platform
from idmtools_cli.iplatform_cli import PlatformCLIPlugins

supported_platforms = PlatformCLIPlugins().get_plugin_map()

tags_help = "Tag to filter by. This should be in the form name value. For example, if you have a tag type=PythonTask " \
            "you would use --tags type PythonTask. In addition, you can provide multiple tags, ie --tags a 1 " \
            "--tags b 2. This will perform an AND based query on the tags meaning only jobs contains ALL the tags " \
            "specified will be displayed"


def show_error(message: Union[str, requests.Response]) -> NoReturn:
    """
    Display an error response from API on the command line.

    Args:
        message (Union[str, requests.Response]): message to display

    Returns:
        Nothing
    """
    print(f'{Fore.RED}Error{Fore.RESET}: {message}')
    sys.exit(-1)


def get_platform_from_config_or_name(config_block, platform):
    """
    Attempt to find the config block or crete platform obj from name.

    Args:
        config_block: Config block
        platform: Platform type

    Returns:
        Platform object
    """
    if platform is None and config_block is None:
        raise UsageError("You must specify a platform or a configuration block")
    if config_block:
        platform_obj = Platform(config_block)
    else:
        platform_obj = supported_platforms[platform].get({})
    return platform_obj
