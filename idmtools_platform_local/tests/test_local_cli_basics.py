# flake8: noqa E402
import re
import time
import unittest.mock
import os
import pytest
from click._compat import strip_ansi
from sqlalchemy.exc import OperationalError

from idmtools.core.platform_factory import Platform
from idmtools_test.utils.decorators import restart_local_platform

api_host = os.getenv('API_HOST', 'localhost')
os.environ['SQLALCHEMY_DATABASE_URI'] = f'postgresql+psycopg2://idmtools:idmtools@{api_host}/idmtools'
from idmtools_test.utils.cli import get_subcommands_from_help_result, run_command
from idmtools_test.utils.local_platform import create_test_data


@pytest.mark.docker
@pytest.mark.local_platform_cli
class TestLocalCLIBasic(unittest.TestCase):

    @classmethod
    @restart_local_platform(silent=True, stop_after=False)
    def setUpClass(cls):
        platform = Platform('Local')
        retries = 0
        while retries < 10:
            try:
                create_test_data()
                break
            except (OperationalError, ConnectionError):
                time.sleep(0.5)
                retries += 1

    @classmethod
    @restart_local_platform(silent=True, stop_before=False)
    def tearDownClass(cls) -> None:
        pass

    def test_load(self):
        result = run_command('experiment', '--platform', 'Local', '--help', base_command='')
        lines = get_subcommands_from_help_result(result)
        # ensure our command is in the options
        self.assertIn('status', lines)

    def test_status(self):
        result = run_command('experiment', '--platform', 'Local', 'status', base_command='')
        print(result)

    @pytest.mark.long
    def test_docker(self):
        """
        Filtering depends on a few postgres filtering method so we have to
        setup a connection to postgres and then test querying
        
        """

        with self.subTest("test_experiments_status"):
            # this is ugly but something odd is going on with db on windows
            # it could be artifacts in tests but it appears db takes a moment to respond with experiments
            time.sleep(10 if os.name == "nt" else 1)

            result = run_command('experiment', '--platform', 'Local', 'status', base_command='')
            self.assertEqual(result.exit_code, 0, f'{result.exit_code} - {result.output}')
            output = re.sub(r'[\+\-]+', '', result.output).split("\n")
            output = [o for o in output if o and len(o) > 3 and 'experiment_id' not in o]
            self.assertEqual(len(output), 3)
            rows = list(map(lambda x: list(map(str.strip, x)), [s.split('|') for s in output]))
            self.assertEqual(rows[0][1], "DDDDD")
            self.assertEqual(rows[1][1], "BBBBB")
            self.assertEqual(rows[2][1], "AAAAA")

        with self.subTest("test_simulation_status"):
            result = run_command('simulation', '--platform', 'Local', 'status', base_command='')
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
