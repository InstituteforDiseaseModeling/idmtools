import os
import tempfile
import unittest.mock
from os.path import join

from sqlalchemy import create_engine

from idmtools_platform_local.workers.brokers import setup_broker


def config_local_test():

    os.environ['UNIT_TESTS'] = '1'
    os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'

    if 'DATA_PATH' not in os.environ:
        test_temp_dir = tempfile.mkdtemp()
        os.environ['DATA_PATH'] = join(test_temp_dir, 'data')
    setup_broker()
    return os.environ['DATA_PATH']


def reset_local_broker():
    if 'UNIT_TESTS' in os.environ:
        del os.environ['UNIT_TESTS']
    if 'SQLALCHEMY_DATABASE_URI' in os.environ:
        del os.environ['SQLALCHEMY_DATABASE_URI']

    if 'DATA_PATH' in os.environ:
        del os.environ['DATA_PATH']


def setup_test_broker():
    pass


def get_test_local_env_overrides():
    overrides = dict()
    if 'run_as' in os.environ:
        overrides['run_as'] = os.environ['run_as']
    return overrides


engine = None


def get_db():
    global  engine
    if engine is None:
        engine = create_engine('sqlite://', pool_size=32)
    return engine


patch_broker = unittest.mock.patch('idmtools_platform_local.local_platform.setup_broker', side_effect=setup_test_broker)
patch_db = unittest.mock.patch('idmtools_platform_local.workers.database.get_db', side_effect=get_db)