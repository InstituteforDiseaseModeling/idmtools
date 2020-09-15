import pytest
import unittest

from idmtools_test.utils.cli import run_command


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
        self.assertIn(f'idmtools: {idm_version}', result.output)
        self.assertIn(f'idmtools cli: {idm_cli_version}', result.output)
        self.assertIn(f'CommandTask: {idm_version}', result.output)
        # test in case we don't have plugins installed
        try:
            from idmtools_models import __version__ as models_version
            self.assertIn(f'JSONConfiguredPythonTask: {models_version}', result.output)
            self.assertIn(f'PythonTask: {models_version}', result.output)
            self.assertIn(f'JSONConfiguredRTask: {models_version}', result.output)
            self.assertIn(f'ScriptWrapperTask: {models_version}', result.output)
            self.assertIn(f'RTask: {models_version}', result.output)
            self.assertIn(f'TemplatedScriptTask: {models_version}', result.output)
        except ImportError:
            pass

        try:
            from idmtools_platform_comps import __version__ as comps_version
            self.assertIn(f'COMPSPlatform: {comps_version}', result.output)
            self.assertIn(f'SSMTPlatform: {comps_version}', result.output)
        except ImportError:
            pass

        try:
            from idmtools_platform_local import __version__ as local_version
            self.assertIn(f'LocalPlatform: {local_version}', result.output)
        except ImportError:
            pass

        try:
            from idmtools_platform_slurm import __version__ as slurm_version
            self.assertIn(f'SlurmPlatform: {slurm_version}', result.output)
        except ImportError:
            pass