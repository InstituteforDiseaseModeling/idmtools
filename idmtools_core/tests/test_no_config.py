import io
import os
import tempfile
import unittest.mock
import pytest


class TestNoConfig(unittest.TestCase):

    def setUp(self) -> None:
        # store current work directory
        super().setUp()
        self.current_directory = os.getcwd()
        self.temp_directory = tempfile.TemporaryDirectory()
        os.chdir(self.temp_directory.name)

    def tearDown(self) -> None:
        self.temp_directory.cleanup()
        os.chdir(self.current_directory)
        try:
            os.unsetenv('IDMTOOLS_ERROR_NO_CONFIG')
        except:
            pass

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    @pytest.mark.comps
    def test_success(self, output):
        from idmtools.config import IdmConfigParser
        from idmtools.core.platform_factory import Platform
        from idmtools.entities.experiment import Experiment
        IdmConfigParser.clear_instance()
        sim_root_dir = os.path.join('$COMPS_PATH(USER)', 'output')
        plat_obj = Platform('COMPS',
                            endpoint='https://comps.idmod.org',
                            environment='Calculon',
                            priority='Normal',
                            simulation_root=sim_root_dir,
                            node_group='idm_abcd',
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
        from idmtools.config import IdmConfigParser
        from idmtools.core.platform_factory import Platform
        from idmtools.entities.experiment import Experiment
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
        os.environ['IDMTOOLS_ERROR_NO_CONFIG'] = '0'
        from idmtools.config import IdmConfigParser
        from idmtools.core.platform_factory import Platform
        from idmtools.entities.experiment import Experiment
        IdmConfigParser.clear_instance()
        plat_obj = Platform('COMPS',
                            endpoint='https://comps2.idmod.org',
                            environment='Bayesian',
                            priority='Normal',
                            simulation_root=sim_root_dir,
                            node_group='emod_abcd',
                            num_cores='1',
                            num_retries='0',
                            exclusive='False')
        experiment = Experiment.from_id('a7ea2ac2-a068-ea11-a2c5-c4346bcb1550')
        self.assertIn("File 'idmtools.ini' Not Found!", output.getvalue())
        # Need to identify how to capture output after log changes
        # self.assertIn("The field num_cores requires a value of type int. You provided <abc>", output.getvalue())

        IdmConfigParser.clear_instance()
