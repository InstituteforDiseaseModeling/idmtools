import json
import os
import sys
import pytest

from idmtools.analysis.platform_anaylsis import PlatformAnalysis
from idmtools.core.platform_factory import Platform
from idmtools_test.utils.decorators import warn_amount_ssmt_image_decorator
from idmtools.core import ItemType


analyzer_path = os.path.join(os.path.dirname(__file__), "..", "inputs")
sys.path.insert(0, analyzer_path)
from population_analyzer import PopulationAnalyzer  # noqa


@pytest.fixture
def platform_slurm_2():
    """
    Provide slurm 2 platform to tests
    Returns:

    """
    return Platform('SLURM2')


@pytest.fixture
def platform_comps2():
    """
    Provide slurm 2 platform to tests
    Returns:

    """
    return Platform('Bayesian')


# Test PopulationAnalyzer with PlatformAnalysis
def do_platform_analysis(platform: Platform):
    if platform.environment.lower() == "bayesian":
        experiment_id = 'd0b75dba-0e18-ec11-92df-f0921c167864'
    elif platform.environment.lower() == "slurmstage":
        experiment_id = 'c348452d-921c-ec11-92e0-f0921c167864'  # comps2 exp id
    analysis = PlatformAnalysis(platform=platform, experiment_ids=[experiment_id],
                                analyzers=[PopulationAnalyzer],
                                analyzers_args=[{'name': ['anything']}],
                                analysis_name='test platformanalysis with analyzer',
                                tags={'idmtools': 'test_tag'},
                                extra_args=dict(max_workers=8))

    analysis.analyze(check_status=True)
    wi = analysis.get_work_item()

    # verify workitem result
    local_output_path = "output"
    out_filenames = [f"output/{experiment_id}/population.json", f"output/{experiment_id}/population.png", "WorkOrder.json"]
    platform.get_files_by_id(wi.uid, ItemType.WORKFLOW_ITEM, out_filenames, local_output_path)

    file_path = os.path.join(local_output_path, wi.id)
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


@pytest.mark.smoke
@warn_amount_ssmt_image_decorator
@pytest.mark.parametrize('platform',
                         [pytest.lazy_fixture('platform_comps2'), pytest.lazy_fixture('platform_slurm_2')])
def test_platformAnalysis(platform: Platform):
    do_platform_analysis(platform)




