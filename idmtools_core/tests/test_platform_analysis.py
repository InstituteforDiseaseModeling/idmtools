import tempfile

import os
from unittest import TestCase
import pytest
from idmtools.analysis.download_analyzer import DownloadAnalyzer as SampleAnalyzer
from idmtools.analysis.platform_anaylsis import PlatformAnalysis
from idmtools.core.platform_factory import Platform


@pytest.mark.smoke
@pytest.mark.serial
class TestPlatformAnalysis(TestCase):
    def test_basic_functionality(self):
        platform = Platform('Test')
        platform_analysis = PlatformAnalysis(platform=platform, analyzers=[SampleAnalyzer], experiment_ids=['3f46b433-1c8b-400f-a0df-f252c8a47329'])
        command = platform_analysis._prep_analyze()

        self.assertEqual(command, 'python platform_analysis_bootstrap.py --experiment-ids 3f46b433-1c8b-400f-a0df-f252c8a47329 --analyzers download_analyzer.DownloadAnalyzer --block Test')

        self.assertEqual(len(platform_analysis.additional_files), 4)
        asset_names = [f.filename for f in platform_analysis.additional_files]
        self.assertIn("platform_analysis_bootstrap.py", asset_names)
        self.assertIn("download_analyzer.py", asset_names)
        self.assertIn("analyzer_args.pkl", asset_names)
        self.assertIn("idmtools.ini", asset_names)

        idmtools_asset = [f for f in platform_analysis.additional_files if f.filename == "idmtools.ini"][0]
        from idmtools import IdmConfigParser
        self.assertEqual(idmtools_asset.absolute_path, IdmConfigParser.get_config_path())

    def test_verbose_command(self):
        platform = Platform('Test')
        platform_analysis = PlatformAnalysis(platform=platform, analyzers=[SampleAnalyzer], experiment_ids=['3f46b433-1c8b-400f-a0df-f252c8a47329'], verbose=True)
        command = platform_analysis._prep_analyze()

        self.assertEqual(command, 'python platform_analysis_bootstrap.py --experiment-ids 3f46b433-1c8b-400f-a0df-f252c8a47329 --analyzers download_analyzer.DownloadAnalyzer --block Test --verbose')

    def test_wrapper_command(self):
        f = tempfile.NamedTemporaryFile(suffix='.sh', mode='w', delete=False)
        f.write("$*")
        platform = Platform('Test')
        platform_analysis = PlatformAnalysis(platform=platform, analyzers=[SampleAnalyzer], experiment_ids=['3f46b433-1c8b-400f-a0df-f252c8a47329'], verbose=True, wrapper_shell_script=f.name)
        command = platform_analysis._prep_analyze()

        self.assertEqual(command, f'/bin/bash {os.path.basename(f.name)} python platform_analysis_bootstrap.py --experiment-ids 3f46b433-1c8b-400f-a0df-f252c8a47329 --analyzers download_analyzer.DownloadAnalyzer --block Test --verbose')

    def test_pre_run_pickle(self):
        platform = Platform('Test')

        def pre_run():
            print('Hello World')
        platform_analysis = PlatformAnalysis(platform=platform, analyzers=[SampleAnalyzer], experiment_ids=['3f46b433-1c8b-400f-a0df-f252c8a47329'], pre_run_func=pre_run)
        command = platform_analysis._prep_analyze()

        self.assertEqual(command, 'python platform_analysis_bootstrap.py --experiment-ids 3f46b433-1c8b-400f-a0df-f252c8a47329 --analyzers download_analyzer.DownloadAnalyzer --pre-run-func pre_run --block Test')
        asset_names = [f.filename for f in platform_analysis.additional_files]
        self.assertIn("platform_analysis_bootstrap.py", asset_names)
        self.assertIn("download_analyzer.py", asset_names)
        self.assertIn("analyzer_args.pkl", asset_names)
        self.assertIn("pre_run.py", asset_names)
