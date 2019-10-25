
import re
import time
import unittest
import unittest.mock
import os
import pytest
from click._compat import strip_ansi
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
api_host = os.getenv('API_HOST', 'localhost')
os.environ['SQLALCHEMY_DATABASE_URI'] = f'postgresql+psycopg2://idmtools:idmtools@{api_host}/idmtools'
from idmtools_platform_local.docker.docker_operations import DockerOperations
from idmtools_platform_local.status import Status
from idmtools_platform_local.workers.utils import create_or_update_status
from idmtools_test.utils.cli import get_subcommands_from_help_result, run_command
from idmtools_test.utils.confg_local_runner_test import get_test_local_env_overrides


class TestLocalCLIBasic(unittest.TestCase):
    @staticmethod
    def create_test_data():
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
                                status=Status.done,
                                extra_details=dict(simulation_type='Python'))
        create_or_update_status('FFFFF', '/data/FFFFF', dict(i='j', k='l'), parent_uuid='DDDDD',
                                status=Status.done,
                                extra_details=dict(simulation_type='Python'))

    @staticmethod
    def run_command(*args, start_command=None, base_command=None):
        if start_command is None:
            start_command = []
        if base_command:
            start_command.append(base_command)
        return run_command(*args, start_command=start_command)

    def test_load(self):
        result = self.run_command('experiment', '--platform', 'Local', '--help', base_command='')
        lines = get_subcommands_from_help_result(result)
        # ensure our command is in the options
        self.assertIn('status', lines)

    def test_status(self):
        result = self.run_command('experiment', '--platform', 'Local', 'status', base_command='')
        print(result)

    @pytest.mark.docker
    def test_docker(self):
        """
        Filtering depends on a few postgres filtering method so we have to
        setup a connection to postgres and then test querying
        """
        # start up postgres
        dm = DockerOperations(**get_test_local_env_overrides())
        dm.cleanup()
        dm.create_services()
        # give services some time to start
        time.sleep(5)
        # ensure we are connecting to proper db
        url = 'postgresql+psycopg2://idmtools:idmtools@localhost/idmtools'
        engine = create_engine(url, echo=False, pool_size=32)
        session_factory = sessionmaker(bind=engine)
        from idmtools_platform_local.workers.data.job_status import Base

        def test_db_factory():
            return session_factory()

        Base.metadata.create_all(engine)

        with self.subTest("test_experiments_status"):
            # Now patch our areas that use our session
            @unittest.mock.patch('idmtools_platform_local.workers.utils.get_session', side_effect=test_db_factory)
            def do_test(*mocks):
                self.create_test_data()
                time.sleep(1)

                result = self.run_command('experiment', '--platform', 'Local', 'status', base_command='')
                self.assertEqual(result.exit_code, 0, f'{result.exit_code} - {result.output}')
                output = re.sub(r'[\+\-]+', '', result.output).split("\n")
                output = [o for o in output if o and len(o) > 3 and 'experiment_id' not in o]
                self.assertEqual(len(output), 3)
                rows = list(map(lambda x: list(map(str.strip, x)), [s.split('|') for s in output]))
                self.assertEqual(rows[0][1], "DDDDD")
                self.assertEqual(rows[1][1], "BBBBB")
                self.assertEqual(rows[2][1], "AAAAA")

            do_test()

        with self.subTest("test_simulation_status"):
            # Now patch our areas that use our session
            def do_test(*mocks):
                result = self.run_command('simulation', '--platform', 'Local', 'status', base_command='')
                self.assertEqual(result.exit_code, 0, f'{result.exit_code} - {result.output}')
                output = re.sub(r'[\+\-]+', '', strip_ansi(result.output)).split("\n")
                output = [o for o in output if o and len(o) > 3 and 'simulation_uid' not in o]
                self.assertEqual(len(output), 3)
                rows = list(map(lambda x: list(map(str.strip, x)), [s.split('|') for s in output]))
                self.assertEqual(rows[0][1], "FFFFF")
                self.assertEqual(rows[0][2], "DDDDD")
                self.assertEqual(rows[0][3], "done")
                self.assertEqual(rows[1][1], "EEEEE")
                self.assertEqual(rows[1][2], "DDDDD")
                self.assertEqual(rows[1][3], "done")
                self.assertEqual(rows[2][1], "CCCCC")
                self.assertEqual(rows[2][2], "BBBBB")
                self.assertEqual(rows[2][3], "created")

            do_test()

        dm.cleanup()
