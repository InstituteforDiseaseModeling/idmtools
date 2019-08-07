import os
import tempfile
from os.path import join


def config_local_test():

    os.environ['UNIT_TESTS'] = '1'
    os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'

    if 'DATA_PATH' not in os.environ:
        test_temp_dir = tempfile.mkdtemp()
        os.environ['DATA_PATH'] = join(test_temp_dir, 'data')
    import idmtools_platform_local.workers.brokers
    return os.environ['DATA_PATH']


def config_local_rest():
    if 'UNIT_TESTS' in os.environ:
        del os.environ['UNIT_TESTS']
    if 'SQLALCHEMY_DATABASE_URI' in os.environ:
        del os.environ['SQLALCHEMY_DATABASE_URI']

    if 'DATA_PATH' in os.environ:
        del os.environ['DATA_PATH']
