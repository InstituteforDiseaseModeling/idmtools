import os
import tempfile
from os.path import join


def config_local_test():
    test_temp_dir = tempfile.mkdtemp()
    os.environ['UNIT_TESTS'] = '1'
    os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
    os.environ['DATA_PATH'] = join(test_temp_dir, 'data')
    import idmtools_platform_local.workers.brokers
    return test_temp_dir

