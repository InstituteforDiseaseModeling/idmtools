# flake8: noqa E402
from idmtools_test.utils.confg_local_runner_test import config_local_test
local_path = config_local_test()
import unittest
from operator import itemgetter
from idmtools_platform_local.workers.ui.app import application
from idmtools_platform_local.workers.utils import create_or_update_status


class TestAPI(unittest.TestCase):

    def setUp(self):
        self.app = application.test_client()

    def test_fetch_experiments(self):
        # ensure we have some phony data

        # this experiment has no children
        create_or_update_status('AAAAA', '/data/AAAA', dict(a='b', c='d'),
                                extra_details=dict(simulation_type='Python'))

        # Experiment
        create_or_update_status('BBBBB', '/data/AAAA', dict(a='b', c='d'),
                                extra_details=dict(simulation_type='Python'))

        # Simulation
        create_or_update_status('CCCCC', '/data/AAAA', dict(a='b', c='d'), parent_uuid='BBBBB',
                                extra_details=dict(simulation_type='Python'))
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

    def test_one_works(self):
        create_or_update_status('AAAAA', '/data/AAAA', dict(a='b', c='d'),
                                extra_details=dict(simulation_type='Python'))
        result = self.app.get('/api/experiments/AAAAA')
        self.assertEqual(200, result.status_code)

        data = result.json
        self.assertIsInstance(data, dict)
        self.assertEqual(data['experiment_id'], 'AAAAA')
        self.assertDictEqual(data['tags'],  dict(a='b', c='d'))
        self.assertEqual(data['data_path'], '/data/AAAA')

    def test_missing_404(self):
        result = self.app.get('/api/experiments/IDontExist')
        self.assertEqual(404, result.status_code)