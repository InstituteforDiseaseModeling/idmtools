import allure
import pytest
import unittest
from idmtools_test.utils.cli import run_command


@allure.story("CLI")
@allure.story("Version")
@allure.suite("idmtools_cli")
class TestSystemInfoBasics(unittest.TestCase):

    @pytest.mark.smoke
    def test_version(self):
        """
        This test is to ensure:
        a) version works
        """
        from idmtools import __version__ as idm_version
        from idmtools_cli import __version__ as idm_cli_version
        result = run_command('version')
        self.assertEqual(0, result.exit_code)
        # Check for our help string
        self.assertIn(f'idmtools                             Version: {idm_version}', result.output)
        self.assertIn(f'idmtools-cli                         Version: {idm_cli_version}', result.output)
        self.assertIn(f'CommandTask', result.output)
        # test in case we don't have plugins installed
        try:
            from idmtools_models import __version__ as models_version
            self.assertIn(f'idmtools-models                      Version: {models_version}', result.output)
            self.assertIn(f'JSONConfiguredPythonTask', result.output)
            self.assertIn(f'PythonTask', result.output)
            self.assertIn(f'JSONConfiguredRTask', result.output)
            self.assertIn(f'ScriptWrapperTask', result.output)
            self.assertIn(f'RTask', result.output)
            self.assertIn(f'TemplatedScriptTask', result.output)
        except ImportError:
            pass

        try:
            from idmtools_platform_comps import __version__ as comps_version
            self.assertIn(f'idmtools-platform-comps              Version: {comps_version}', result.output)
            self.assertIn(f'COMPSPlatform', result.output)
            self.assertIn(f'SSMTPlatform', result.output)
        except ImportError:
            pass

        try:
            from idmtools_platform_slurm import __version__ as slurm_version
            self.assertIn(f'idmtools-platform-slurm              Version: {slurm_version}', result.output)
            self.assertIn(f'SlurmPlatform', result.output)
        except ImportError:
            pass