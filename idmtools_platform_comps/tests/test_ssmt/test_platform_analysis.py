import json
import os
import shutil
import sys
import tempfile

import pytest

from idmtools.analysis.platform_anaylsis import PlatformAnalysis
from idmtools.core.platform_factory import Platform
from idmtools_test.utils.decorators import warn_amount_ssmt_image_decorator
from idmtools.core import ItemType
from idmtools.analysis.download_analyzer import DownloadAnalyzer
from .get_latest_ssmt_image import get_latest_image_stage

analyzer_path = os.path.join(os.path.dirname(__file__), "..", "inputs")
sys.path.insert(0, analyzer_path)
from population_analyzer import PopulationAnalyzer  # noqa


@pytest.fixture
def platform_slurm_2():
    """
    Provide slurm 2 platform to tests
    Returns:

    """
    return Platform('SLURMSTAGE', docker_image="idm-docker-staging.packages.idmod.org/idmtools/comps_ssmt_worker:" +
                                               get_latest_image_stage())


@pytest.fixture
def platform_comps2():
    """
    Provide slurm 2 platform to tests
    Returns:

    """
    return Platform('BAYESIAN', docker_image="idm-docker-staging.packages.idmod.org/idmtools/comps_ssmt_worker:" + get_latest_image_stage())


# Test PlatformAnalysis with PopulationAnalyzer for experiment id
def do_platform_analysis_experiment(platform: Platform):
    if platform.environment.lower() == "bayesian":
        experiment_id = 'd0b75dba-0e18-ec11-92df-f0921c167864' # comps2 exp id
    elif platform.environment.lower() == "slurmstage":
        experiment_id = 'c348452d-921c-ec11-92e0-f0921c167864'  # comps2 exp id

    # Run ssmt PlatformAnalysis with an experiment id which will run PopulationAnalyzer in COMPS docker worker
    analysis = PlatformAnalysis(platform=platform, experiment_ids=[experiment_id],
                                analyzers=[PopulationAnalyzer],
                                analyzers_args=[{'name': ['anything']}],
                                analysis_name='test platformanalysis with experiment',
                                tags={'idmtools': 'test_tag'},
                                extra_args={"max_workers":8})

    analysis.analyze(check_status=True)
    wi = analysis.get_work_item()
    assert wi.succeeded == True

    # Verify PlatformAnalysis workitem result
    try:
        dirpath = tempfile.mkdtemp()
        out_filenames = [f"output/{experiment_id}/population.json", f"output/{experiment_id}/population.png", "WorkOrder.json"]
        # Retrieve files to local temp dir
        platform.get_files_by_id(wi.uid, ItemType.WORKFLOW_ITEM, out_filenames, dirpath)

        # Asset files
        file_path = os.path.join(dirpath, wi.id)
        assert os.path.exists(os.path.join(file_path, "output", experiment_id, "population.json"))
        assert os.path.exists(os.path.join(file_path, "WorkOrder.json"))
        worker_order = json.load(open(os.path.join(file_path, "WorkOrder.json"), 'r'))
        assert worker_order['WorkItem_Type'] == "DockerWorker"
        execution = worker_order['Execution']
        base_cmd = f"python3 platform_analysis_bootstrap.py " \
                   f"--experiment-ids {experiment_id} " \
                   f"--analyzers population_analyzer.PopulationAnalyzer " \
                   f"--analyzer-manager-args-file extra_args.pkl " \
                   f"--platform-args platform_args.pkl " \
                   f"--block {platform._config_block}_SSMT"

        assert execution['Command'] == base_cmd
    finally:
        shutil.rmtree(dirpath)


# Test PlatformAnalysis with DownloadAnalyzer for workitem id
def do_platform_analysis_wi(platform: Platform):
    if platform.environment.lower() == "bayesian":
        workitem_id = '22afccb1-d31f-ec11-92e0-f0921c167864'  # comps2 exp id
    elif platform.environment.lower() == "slurmstage":
        workitem_id = 'fe6a80b9-d31f-ec11-92e0-f0921c167864'  # comps2 exp id

    # Run ssmt PlatformAnalysis for DownloadAnalyzer in COMPS with a workitem id
    # This will download stdout.txt and stderr.txt with original workitem_id with new workitem in comps
    analysis = PlatformAnalysis(platform=platform, work_item_ids=[workitem_id],
                                analyzers=[DownloadAnalyzer],
                                analyzers_args=[{'filenames': ['stdout.txt', 'stderr.txt']}],
                                analysis_name="test platformanalysis with workitem")

    analysis.analyze(check_status=True)
    wi = analysis.get_work_item()
    assert wi.succeeded == True
    # Verify PlatformAnalysis result
    try:
        # Retrieve files to local temp dir
        dirpath = tempfile.mkdtemp()
        out_filenames = [f"output/{workitem_id}/stdout.txt", f"output/{workitem_id}/stderr.txt", "WorkOrder.json"]
        platform.get_files_by_id(wi.uid, ItemType.WORKFLOW_ITEM, out_filenames, dirpath)

        file_path = os.path.join(dirpath, wi.id)
        assert os.path.exists(os.path.join(file_path, "output", workitem_id, "stdout.txt"))
        assert os.path.exists(os.path.join(file_path, "output", workitem_id, "stderr.txt"))
        assert os.path.exists(os.path.join(file_path, "WorkOrder.json"))
        worker_order = json.load(open(os.path.join(file_path, "WorkOrder.json"), 'r'))
        assert worker_order['WorkItem_Type'] == "DockerWorker"
        execution = worker_order['Execution']
        base_cmd = f"python3 platform_analysis_bootstrap.py " \
                   f"--work-item-ids {workitem_id} " \
                   f"--analyzers download_analyzer.DownloadAnalyzer " \
                   f"--analyzer-manager-args-file extra_args.pkl " \
                   f"--platform-args platform_args.pkl " \
                   f"--block {platform._config_block}_SSMT"

        assert execution['Command'] == base_cmd

    finally:
        shutil.rmtree(dirpath)


@pytest.mark.smoke
@pytest.mark.ssmt
@warn_amount_ssmt_image_decorator
@pytest.mark.parametrize('platform',
                         [pytest.lazy_fixture('platform_comps2'), pytest.lazy_fixture('platform_slurm_2')])
def test_platform_analysis(platform: Platform):
    do_platform_analysis_experiment(platform)


@pytest.mark.smoke
@pytest.mark.ssmt
@warn_amount_ssmt_image_decorator
@pytest.mark.parametrize('platform',
                         [pytest.lazy_fixture('platform_comps2'), pytest.lazy_fixture('platform_slurm_2')])
def test_platform_analysis_workitem(platform: Platform):
    do_platform_analysis_wi(platform)



import allure
import unittest.mock
from idmtools_test.utils.utils import get_case_name
from idmtools_platform_comps.comps_platform import COMPSPlatform
from idmtools_platform_comps.ssmt_platform import SSMTPlatform

@pytest.mark.comps
@pytest.mark.serial
@pytest.mark.ssmt
class TestSSMTPlatform(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.case_name = get_case_name(os.path.basename(__file__) + "--" + self._testMethodName)
        self.platform = Platform('BAYESIAN')

    def tearDown(self):
        super().tearDown()

    @allure.feature("ssmt platform")
    def test_ssmt_platform(self):
        ssmt_platform = Platform("BAYESIAN_SSMT")
        self.assertTrue(isinstance(ssmt_platform, SSMTPlatform))
        self.assertTrue(isinstance(ssmt_platform, COMPSPlatform))

        comps_platform = Platform("BAYESIAN")
        self.assertTrue(isinstance(comps_platform, COMPSPlatform))
        self.assertFalse(isinstance(comps_platform, SSMTPlatform))

    @allure.feature("ssmt platform")
    def test_ssmt_platform_specification(self):
        from idmtools_platform_comps.plugin_info import SSMTPlatformSpecification
        ssmt_spec = SSMTPlatformSpecification()
        _aliases = ssmt_spec.get_configuration_aliases()
        self.assertIn("BAYESIAN_SSMT", _aliases)

    @allure.feature("ssmt platform")
    def test_comps_platform_pecification(self):
        from idmtools_platform_comps.plugin_info import COMPSPlatformSpecification
        comps_spec = COMPSPlatformSpecification()
        _aliases = comps_spec.get_configuration_aliases()
        self.assertNotIn("BAYESIAN_SSMT", _aliases)

    @allure.feature("ssmt platform")
    def test_platformP_ugins(self):
        from idmtools.registry.platform_specification import PlatformPlugins
        _platforms = PlatformPlugins().get_plugin_map()
        _aliases = PlatformPlugins().get_aliases()

        self.assertIn("SSMT", _platforms)
        self.assertIn("BAYESIAN_SSMT", _aliases)
