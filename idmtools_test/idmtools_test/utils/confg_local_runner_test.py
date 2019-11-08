import os
import tempfile
import unittest.mock
from importlib import reload
from os.path import join


def config_local_test():
    from idmtools_platform_local.internals.workers.brokers import setup_broker, close_brokers
    close_brokers()
    os.environ['UNIT_TESTS'] = '1'
    if 'DATA_PATH' not in os.environ:
        test_temp_dir = tempfile.mkdtemp()
        os.environ['DATA_PATH'] = join(test_temp_dir, 'data')
    setup_broker()
    return os.environ['DATA_PATH']


def reset_local_broker():
    from idmtools_platform_local.internals.workers.brokers import close_brokers

    if 'UNIT_TESTS' in os.environ:
        del os.environ['UNIT_TESTS']

    if 'SQLALCHEMY_DATABASE_URI' in os.environ:
        del os.environ['SQLALCHEMY_DATABASE_URI']

    if 'DATA_PATH' in os.environ:
        del os.environ['DATA_PATH']
    close_brokers()
    try:
        from idmtools_platform_local.internals.workers.brokers import setup_broker
        setup_broker(10)
        import idmtools_platform_local.internals.tasks.create_experiment as ce
        import idmtools_platform_local.internals.tasks.create_simulation as cs
        import idmtools_platform_local.internals.tasks.general_task as gt
        import idmtools_platform_local.internals.tasks.docker_run as dr
        import dramatiq.broker as db
        import dramatiq as dm
        for m in [db, dm, cs, ce, gt, dr]:
            reload(m)

    except ModuleNotFoundError as e:
        print(e)
        pass


def setup_test_broker():
    pass


def get_test_local_env_overrides():
    overrides = dict()
    if 'run_as' in os.environ:
        overrides['run_as'] = os.environ['run_as']
    return overrides


engine = None


def get_db():
    from sqlalchemy import create_engine
    global engine
    if engine is None:
        engine = create_engine('sqlite://', pool_size=32)
    return engine


patch_broker = unittest.mock.patch('idmtools_platform_local.internals.workers.brokers.setup_broker', side_effect=setup_test_broker)
patch_db = unittest.mock.patch('idmtools_platform_local.internals.workers.database.get_db', side_effect=get_db)
