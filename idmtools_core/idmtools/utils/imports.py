import glob
from os.path import join, dirname, basename, isfile
from typing import List


def get_modules_from_file(file: str) -> List[str]:
    """
    Get all modules from the same level of the specified file. This should be used in __init__ modules.

    Examples:
        ``
        from idmtools.utils.imports import get_modules_from_file
        # load all the files in the current directory
        __all__ = get_modules_from_file(__file__)
        ``

    Args:
        file(str): Where file is located. Usually you will call with *__file__*
        assume_nested_obj(bool): Assume the filename contains an object of the same name. For example,
        IExperiment.py contains IExperiment

    Returns:
        (List[str]) Modules loaded from directory
    """
    modules = glob.glob(join(dirname(file), "*.py"))
    return [basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]
