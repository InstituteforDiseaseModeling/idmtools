from logging import getLogger

import allure
import io
import os
import unittest.mock
import pytest
from idmtools_test.utils.decorators import run_in_temp_dir
from idmtools.config import IdmConfigParser
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment

logger = getLogger(__name__)


@pytest.mark.smoke
@allure.story("COMPS")
@allure.story("Configuration")
@allure.suite("idmtools_platform_comps")
@pytest.mark.serial
class TestNoConfig(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.current_directory = os.getcwd()

    def setUp(self) -> None:
        if 'IDMTOOLS_CONFIG_FILE' in os.environ:
            del os.environ['IDMTOOLS_CONFIG_FILE']
        os.environ['IDMTOOLS_ERROR_NO_CONFIG'] = 't'
        os.environ['IDMTOOLS_NO_CONFIG_WARNING'] = '0'
        IdmConfigParser.clear_instance()

    @classmethod
    def tearDownClass(cls) -> None:
        try:
            if 'IDMTOOLS_ERROR_NO_CONFIG' in os.environ:
                del os.environ['IDMTOOLS_ERROR_NO_CONFIG']
            if 'IDMTOOLS_NO_CONFIG_WARNING' in os.environ:
                del os.environ['IDMTOOLS_NO_CONFIG_WARNING']
        except:
            pass
        os.chdir(cls.current_directory)
        IdmConfigParser.clear_instance()

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    @pytest.mark.comps
    @pytest.mark.serial
    @run_in_temp_dir
    def test_success(self, output):
        logger.info(f'Current Directory: {os.getcwd()}')
        logger.info(f'Current idmtools file: {IdmConfigParser.get_config_path()}')
        sim_root_dir = os.path.join('$COMPS_PATH(USER)', 'output')
        plat_obj = Platform('COMPS',
                            endpoint='https://comps2.idmod.org',
                            environment='Bayesian',
                            priority='Normal',
                            simulation_root=sim_root_dir,
                            node_group='emod_abcd',
                            num_cores='1',
                            num_retries='0',
                            exclusive='False', missing_ok=True)

        # we don't care if we find experiment, only that the platform initialized
        try:
            experiment = Experiment.from_id('a7ea2ac2-a068-ea11-a2c5-c4346bcb1550')
        except:  # noqa: E722
            pass
        self.assertIn("File 'idmtools.ini' Not Found!", output.getvalue())

    @pytest.mark.comps
    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    @run_in_temp_dir
    def test_failure(self, output):
        logger.info(f'Current Directory: {os.getcwd()}')
        sim_root_dir = os.path.join('$COMPS_PATH(USER)', 'output')
        with self.assertRaises(ValueError) as a:
            plat_obj = Platform('COMPS',
                                endpoint='https://comps2.idmod.org',
                                environment='Bayesian',
                                priority='Normal',
                                simulation_root=sim_root_dir,
                                node_group='emod_abcd',
                                num_cores='abc',
                                num_retries='0',
                                exclusive='False', missing_ok=True)
            experiment = Experiment.from_id('a7ea2ac2-a068-ea11-a2c5-c4346bcb1550')
        self.assertIn("File 'idmtools.ini' Not Found!", output.getvalue())
        # Need to identify how to capture output after log changes
        # self.assertIn("The field num_cores requires a value of type int. You provided <abc>", output.getvalue())

    @pytest.mark.comps
    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    @run_in_temp_dir
    def test_env_success(self, output):
        logger.info(f'Current Directory: {os.getcwd()}')
        sim_root_dir = os.path.join('$COMPS_PATH(USER)', 'output')
        plat_obj = Platform('COMPS',
                            endpoint='https://comps2.idmod.org',
                            environment='Bayesian',
                            priority='Normal',
                            simulation_root=sim_root_dir,
                            node_group='emod_abcd',
                            num_cores='1',
                            num_retries='0',
                            exclusive='False',
                            missing_ok=True
                            )
        try:
            experiment = Experiment.from_id('a7ea2ac2-a068-ea11-a2c5-c4346bcb1550')
        except RuntimeError as ex:
            # ignore error is it is comps error about not finding id
            if "404 Not Found" in ex.args[0]:
                pass
        self.assertIn("File 'idmtools.ini' Not Found!", output.getvalue())
        # Need to identify how to capture output after log changes
        # self.assertIn("The field num_cores requires a value of type int. You provided <abc>", output.getvalue())
