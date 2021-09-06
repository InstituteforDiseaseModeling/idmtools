import json
import shutil
from logging import getLogger
from pathlib import Path
from uuid import UUID
import pytest

from idmtools.assets.asset_collection import AssetCollection
from idmtools.entities import Suite
from idmtools.entities.iworkflow_item import IWorkflowItem
from idmtools.entities.simulation import Simulation
from .utils import comps_decorate_test

logger = getLogger(__name__)

#  add our feature and ensure we run tests on slurm on comps2
suite_parameterize_decorator = comps_decorate_test('list-files')(pytest.mark.parametrize('suite', [pytest.lazy_fixture('python_files_and_assets_slurm2'), pytest.lazy_fixture('python_files_and_assets_comps2')]))

EXPECTED_FILES_PER_SIMULATION_MODEL1_SIM = 4
EXPECTED_SIMULATIONS_PER_EXPERIMENT_MODEL1_SIM = 4
EXPECTED_ASSETS_PER_MODEL1_EXPERIMENT = 1
EXPECTED_EXPERIMENT_PER_MODEL1_SUITE = 2


@suite_parameterize_decorator
def test_list_files_suite(suite: Suite):
    """
    Test fetching suite assets and children assets
    Uses Fixture: test_model1_files_and_assets
    """
    s: Suite = suite
    suite_assets = s.list_assets()
    assert 0 == len(suite_assets)

    # check is experiment has one asset
    for experiment in s.experiments:
        experiment_assets = experiment.list_assets()
        assert EXPECTED_ASSETS_PER_MODEL1_EXPERIMENT == len(experiment_assets)

    # gather all children assets
    suite_assets = s.list_assets(children=True)
    assert 1 == len(suite_assets)
    assert all([x.filename == "model1.py" for x in suite_assets])

    # test filter of assets with no results
    suite_assets = s.list_assets(children=True, filters=['NotHere'])
    assert 0 == len(suite_assets)

    # test patterns
    suite_assets = s.list_assets(children=True, filters=['*.py'])
    assert 1 == len(suite_assets)

    # gather all files
    suite_files = s.list_files()
    assert 0 == len(suite_files)

    # list all files including children
    suite_files = s.list_files(children=True)
    assert EXPECTED_FILES_PER_SIMULATION_MODEL1_SIM * EXPECTED_EXPERIMENT_PER_MODEL1_SUITE * EXPECTED_SIMULATIONS_PER_EXPERIMENT_MODEL1_SIM == len(suite_files)

    # test list children files(preserve structure)
    suite_files = s.list_children_files()
    # 2 experiments
    assert EXPECTED_EXPERIMENT_PER_MODEL1_SUITE == len(suite_files.keys())

    for experiment, simulations in suite_files.items():
        # each experiment with 6 simulations
        assert EXPECTED_SIMULATIONS_PER_EXPERIMENT_MODEL1_SIM == len(simulations)
        for simulation, files in simulations.items():
            assert EXPECTED_FILES_PER_SIMULATION_MODEL1_SIM == len(files)

    # filter child items
    suite_files = s.list_files(children=True, filters='stderr.txt')
    assert 8 == len(suite_files)
    assert all([x.filename == "stderr.txt" for x in suite_files]) is True

    # check filtering by custom function, by case insensitive match, and by pattern
    # custom function
    def filter_func(file_str: str):
        return ".txt" in file_str

    for filters in [['StDeRR.txt', 'sTdOut.txt'], filter_func, "*.txt"]:
        suite_files = s.list_files(children=True, filters=filters)
        assert 16 == len(suite_files)
        assert all([x.filename in ["stderr.txt", "stdout.txt"] for x in suite_files]) is True

    # test filter for multiple patterns
    suite_files = s.list_files(children=True, filters=['*.txt', '*.json'])
    assert EXPECTED_FILES_PER_SIMULATION_MODEL1_SIM * EXPECTED_EXPERIMENT_PER_MODEL1_SUITE * EXPECTED_SIMULATIONS_PER_EXPERIMENT_MODEL1_SIM == len(suite_files)


@suite_parameterize_decorator
def test_list_files_experiment(suite: Suite):
    """
    Test fetching experiment assets and children assets
    Uses Fixture: test_model1_files_and_assets
    """
    e = suite.experiments[0]
    logger.warning(f"Running test_list_files_experiment from {e.id}")

    # get assets. Force the load so we don't have to reload the whole experiment
    experiment_assets = e.list_assets(reload=True)

    assert EXPECTED_ASSETS_PER_MODEL1_EXPERIMENT == len(experiment_assets)
    assert experiment_assets[0].filename == "model1.py"
    assert experiment_assets[0].absolute_path is None
    assert experiment_assets[0].checksum == UUID('926ee7aa-4f29-bc94-ff99-8c5f83a6d85a')
    experiment_files = e.list_files()

    assert 0 == len(experiment_files)

    # Test loading simulation assets
    experiment_file_with_children = e.list_files(children=True)
    assert EXPECTED_FILES_PER_SIMULATION_MODEL1_SIM * EXPECTED_SIMULATIONS_PER_EXPERIMENT_MODEL1_SIM == len(experiment_file_with_children)
    assert EXPECTED_FILES_PER_SIMULATION_MODEL1_SIM == len([a for a in experiment_file_with_children if a.filename == "config.json"])
    assert EXPECTED_FILES_PER_SIMULATION_MODEL1_SIM == len([a for a in experiment_file_with_children if a.filename == "result.json" and a.relative_path == "output"])
    assert EXPECTED_FILES_PER_SIMULATION_MODEL1_SIM == len([a for a in experiment_file_with_children if a.filename.lower() == "stderr.txt"])
    assert EXPECTED_FILES_PER_SIMULATION_MODEL1_SIM == len([a for a in experiment_file_with_children if a.filename.lower() == "stdout.txt"])

    # test children files which preserves the structure
    experiment_list_children_files = e.list_children_files()
    assert len(experiment_list_children_files.keys()) == EXPECTED_SIMULATIONS_PER_EXPERIMENT_MODEL1_SIM
    assert EXPECTED_FILES_PER_SIMULATION_MODEL1_SIM == len(list(experiment_list_children_files.values())[0])
    assert EXPECTED_FILES_PER_SIMULATION_MODEL1_SIM == len(list(experiment_list_children_files.values())[1])


@suite_parameterize_decorator
def test_list_files_simulation(suite: Suite):
    """
    Test list files for simulations

    Args:
        suite: Our fixture with a python model(model1) have ran on existing environment

    """
    e = suite.experiments[0]
    logger.warning(f"Running test_list_files_simulation from {e.id}")

    sim: Simulation = e.simulations[0]
    files = sim.list_files()

    # Assert each simulation as stdout.txt, stderr.txt, result.json, config.json
    assert len(files) == EXPECTED_FILES_PER_SIMULATION_MODEL1_SIM

    for file in ['stdout.txt', 'stderr.txt', 'output/result.json', 'config.json']:
        assert file in [x.short_remote_path() for x in files]


@suite_parameterize_decorator
def test_list_files_download(suite: Suite):
    """
    Test list of files for download

    Args:
        suite:

    """
    e = suite.experiments[0]
    logger.warning(f"Running test_list_files_download from {e.id}")

    # test creating with just the download directory. We should end up with output directory/
    sim: Simulation = e.simulations[0]
    target_file = sim.list_files()[0]
    resulting_file = Path(f"test_list_files_download/{target_file.filename}")
    if resulting_file.exists():
        shutil.rmtree(resulting_file.parent)
    target_file.download_to_path("test_list_files_download/")
    assert resulting_file.exists()
    # test the file with relative path creates full tree
    shutil.rmtree(resulting_file.parent)
    resulting_file = Path(f"test_list_files_download/{target_file.short_remote_path()}")
    if not target_file.relative_path:
        for x in sim.list_files():
            if x.relative_path:
                target_file = x
                break
    target_file.download_to_path("test_list_files_download/", include_relative_path=True)
    assert resulting_file.exists()


@comps_decorate_test('list-files')
def test_list_files_work_item(ssmt_workitem_python_hello: IWorkflowItem):
    wi = ssmt_workitem_python_hello
    logger.warning(f"Running test_list_files_download from {wi.id}")

    work_item_assets = wi.list_assets()
    assert 1 == len(work_item_assets)
    assert work_item_assets[0].filename == "hello.py"

    # verify work-item output files
    out_filenames = ['stdout.txt', 'stderr.txt', 'WorkOrder.json', 'COMPS_log.log']  # files to retrieve from work-item dir
    work_item_files = wi.list_files()
    for file in out_filenames:
        assert file in [x.filename for x in work_item_files]

    # verify that WorkOrder.json content is correct
    # first stream contents from asset into json dict
    work_order_file = [x for x in work_item_files if x.filename == "WorkOrder.json"][0]
    work_order = json.loads(work_order_file.download_stream().getvalue().decode('utf-8'))
    logger.info(work_order)

    # test download
    expected_path = Path("test_list_files_work_item_download/WorkOrder.json")
    if expected_path.exists():
        shutil.rmtree(expected_path.parent)
    work_order_file.download_to_path(str(expected_path.parent) + "/")
    assert expected_path.exists() is True


@comps_decorate_test('list-files')
@pytest.mark.parametrize('python_ac', [pytest.lazy_fixture('python_ac_on_slurm2'), pytest.lazy_fixture('python_ac_on_comp2')])
def test_list_files_ac(python_ac: AssetCollection):
    list_assets = python_ac.list_assets()

    assert len(list_assets) == 4

    filtered_assets = python_ac.list_assets(filters=["MyExternalLibrary/**"])
    assert len(filtered_assets) == 2
