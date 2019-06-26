from importlib import import_module
from os.path import dirname, basename, isfile, join
import glob
modules = glob.glob(join(dirname(__file__), "*.py"))
__all__ = [basename(f)[:-3]for f in modules if isfile(f) and not f.endswith('__init__.py')]
#actors = [ import_module(f'.{basename(f)[:-3]}', __name__) for f in modules if isfile(f) and not f.endswith('__init__.py')]