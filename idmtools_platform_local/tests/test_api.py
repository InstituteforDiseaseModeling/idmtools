
import time

import pytest

from idmtools_test.utils.confg_local_runner_test import config_local_test, patch_broker, patch_db
import unittest
import unittest.mock

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from idmtools_platform_local.docker.DockerOperations import DockerOperations
from operator import itemgetter

from idmtools_platform_local.workers.utils import create_or_update_status


class TestAPI(unittest.TestCase):

    @patch_broker
    @patch_db
    def setUp(self, mock_broker, mock_db):
        local_path = config_local_test()  # noqa: F841
        config_local_test()
        from idmtools_platform_local.workers.ui.config import application
        self.app = application.test_client()
        self.create_test_data()

    @staticmethod
    def create_test_data():
        from idmtools_platform_local.workers.database import get_session
        from idmtools_platform_local.workers.data.job_status import JobStatus
        # delete any previous data
        get_session().query(JobStatus).delete()
        # this experiment has no children
        create_or_update_status('AAAAA', '/data/AAAAA', dict(a='b', c='d'),
                                extra_details=dict(simulation_type='Python'))
        # Experiment
        create_or_update_status('BBBBB', '/data/BBBBB', dict(e='f', g='h'),
                                extra_details=dict(simulation_type='Python'))
        # Simulation
        create_or_update_status('CCCCC', '/data/CCCCC', dict(i='j', k='l'), parent_uuid='BBBBB',
                                extra_details=dict(simulation_type='Python'))
        # Experiment
        create_or_update_status('DDDDD', '/data/DDDD', dict(e='f', c='d'),
                                extra_details=dict(simulation_type='Python'))

        # Simulation
        create_or_update_status('EEEEE', '/data/EEEEE', dict(i='j', k='l'), parent_uuid='DDDDD',
                                extra_details=dict(simulation_type='Python'))
        create_or_update_status('FFFFF', '/data/FFFFF', dict(i='j', k='l'), parent_uuid='DDDDD',
                                extra_details=dict(simulation_type='Python'))

    def test_fetch_experiments(self):
        # ensure we have some phony data

        result = self.app.get('/api/experiments')
        self.assertEqual(200, result.status_code)

        data = result.json
        self.assertIsInstance(data, list)
        # ensure we know the order for testing
        data = sorted(data, key=itemgetter('experiment_id'))

        self.assertEqual(data[0]['experiment_id'], 'AAAAA')
        # make sure our simulation is not in our experiment list
        self.assertNotIn('CCCCC', map(itemgetter('experiment_id'), data))
        self.assertEqual(data[1]['experiment_id'], 'BBBBB')
        self.assertEqual(len(data[1]['progress']), 1)
        self.assertIn('created', data[1]['progress'][0])
        self.assertEqual(data[1]['progress'][0]['created'], 1)

    def test_fetch_one_experiment_works(self):
        result = self.app.get('/api/experiments/AAAAA')
        self.assertEqual(200, result.status_code)

        data = result.json
        self.assertIsInstance(data, dict)
        self.assertEqual(data['experiment_id'], 'AAAAA')
        self.assertDictEqual(data['tags'], dict(a='b', c='d'))
        self.assertEqual(data['data_path'], '/data/AAAAA')

    def test_fetch_simulations(self):
        # ensure we have some phony data

        result = self.app.get('/api/simulations')
        self.assertEqual(200, result.status_code)

        data = result.json
        self.assertIsInstance(data, list)
        # ensure we know the order for testing
        data = sorted(data, key=itemgetter('simulation_uid'))

        self.assertEqual(data[0]['simulation_uid'], 'CCCCC')
        # make sure our simulation is not in our experiment list
        self.assertNotIn('AAAAA', map(itemgetter('simulation_uid'), data))
        self.assertEqual(data[0]['experiment_id'], 'BBBBB')

        result = self.app.get('/api/simulations', query_string=dict(experiment_id='DDDDD'))
        self.assertEqual(200, result.status_code)

        data = result.json
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)

    def test_fetch_one_simulation_works(self):
        result = self.app.get('/api/simulations/CCCCC')
        self.assertEqual(200, result.status_code)

        data = result.json
        self.assertIsInstance(data, dict)
        self.assertEqual(data['simulation_uid'], 'CCCCC')
        self.assertEqual(data['experiment_id'], 'BBBBB')
        self.assertDictEqual(data['tags'], dict(i='j', k='l'))
        self.assertEqual(data['data_path'], '/data/CCCCC')

    @pytest.mark.docker
    def test_experiment_filtering(self):
        """
        Filtering depends on a few postgres filtering method so we have to
        setup a connection to postgres and then test querying
        """
        # start up postgres
        dm = DockerOperations()
        dm.cleanup(True)
        dm.get_postgres()
        # give postgres 5 seconds to start
        time.sleep(8)
        # ensure we are connecting to proper db
        url = 'postgresql+psycopg2://idmtools:idmtools@localhost/idmtools'
        engine = create_engine(url, echo=True, pool_size=32)
        session_factory = sessionmaker(bind=engine)
        from idmtools_platform_local.workers.data.job_status import Base

        def test_db_factory():
            return session_factory()
        Base.metadata.create_all(engine)

        # Now patch our areas that use our session
        @unittest.mock.patch('idmtools_platform_local.workers.ui.controllers.experiments.get_session', side_effect=test_db_factory)
        @unittest.mock.patch('idmtools_platform_local.workers.utils.get_session', side_effect=test_db_factory)
        def do_test(*mocks):
            self.create_test_data()
            # reset our config to default. This should connect to the postgres db as well
            from idmtools_platform_local.workers.ui.config import application
            other_app = application.test_client()
            result = other_app.get('/api/experiments', query_string=dict(tags='a,b'))
            self.assertEqual(200, result.status_code)
            data = result.json
            self.assertIsInstance(data, list)
            self.assertEqual(len(result.json), 1)

            result = other_app.get('/api/experiments', query_string=dict(tags='a,c'))
            self.assertEqual(200, result.status_code)
            data = result.json
            self.assertIsInstance(data, list)
            self.assertEqual(len(result.json), 0)
        do_test()

        dm.stop_services()
