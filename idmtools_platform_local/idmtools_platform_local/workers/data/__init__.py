import importlib
from os.path import dirname, basename, isfile
import glob
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Find all the modules and import here. This will allow statments like
# from idmtools_local.data import *
modules = glob.glob(dirname(__file__) + "/*.py")
__all__ = [importlib.import_module('{}.{}'.format(__name__, basename(f)[:-3])) for f in modules if
           isfile(f) and not f.endswith('__init__.py')]
