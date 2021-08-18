import allure
import io
import os
import tempfile
import unittest.mock
import pytest
from idmtools.config import IdmConfigParser
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment


@pytest.mark.smoke
@allure.story("COMPS")
@allure.story("Configuration")
@allure.suite("idmtools_platform_comps")
@pytest.mark.serial
class TestNoConfig(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        os.environ['IDMTOOLS_NO_CONFIG_WARNING'] = '0'
        cls.current_directory = os.getcwd()
        cls.temp_directory = tempfile.TemporaryDirectory()
        os.chdir(cls.temp_directory.name)

    @classmethod
    def tearDownClass(cls) -> None:
        try:
            del os.environ['IDMTOOLS_ERROR_NO_CONFIG']
            # try to cleanup but be ok with failures
            cls.temp_directory.cleanup()
        except:
            pass
        os.chdir(cls.current_directory)
        IdmConfigParser.clear_instance()

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    @pytest.mark.comps
    @pytest.mark.serial
    def test_success(self, output):

        IdmConfigParser.clear_instance()
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
    def test_failure(self, output):
        IdmConfigParser.clear_instance()
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
    def test_env_success(self, output):
        sim_root_dir = os.path.join('$COMPS_PATH(USER)', 'output')
        os.environ['IDMTOOLS_NO_CONFIG_WARNING'] = '0'
        IdmConfigParser.clear_instance()
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
