from idmtools.utils.display.settings import *  # noqa: F401, F403
from idmtools.utils.display.displays import *  # noqa: F401, F403


def display(obj, settings):
    for setting in settings:
        print(setting.display(obj))
