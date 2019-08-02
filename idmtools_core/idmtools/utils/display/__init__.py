from idmtools.utils.imports import get_modules_from_file
# load all the files in the current directory
__all__ = get_modules_from_file(__file__)


def display(obj, settings):
    for setting in settings:
        print(setting.display(obj))
