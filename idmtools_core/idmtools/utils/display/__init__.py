"""
root of display utilities for idmtools.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from idmtools.utils.display.settings import *  # noqa: F401, F403
from idmtools.utils.display.displays import *  # noqa: F401, F403


def display(obj, settings):
    """
    Display an object using our settings.

    Args:
        obj: Obj to display
        settings: Display settings

    Returns:
        None
    """
    for setting in settings:
        print(setting.display(obj))
