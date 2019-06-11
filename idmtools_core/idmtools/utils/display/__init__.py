from idmtools.utils.display.settings import *
from idmtools.utils.display.displays import *

def display(obj, settings):
    for setting in settings:
        print(setting.display(obj))
