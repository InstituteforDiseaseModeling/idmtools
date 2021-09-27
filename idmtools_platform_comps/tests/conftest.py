import json
import os
from datetime import datetime, timezone
from logging import getLogger
from pathlib import Path

import pytest
from COMPS.Data import QueryCriteria, Experiment as COMPSExperiment, Suite as COMPSSuite, WorkItem as COMPSWorkItem

from idmtools.assets import AssetCollection, Asset
from idmtools.builders import SimulationBuilder
from idmtools.core import TRUTHY_VALUES, ItemType
from idmtools.core.platform_factory import Platform
from idmtools.entities.command_task import CommandTask
from idmtools.entities.generic_workitem import GenericWorkItem
from idmtools.entities.suite import Suite
from idmtools.entities.experiment import Experiment
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_platform_comps.ssmt_work_items.comps_workitems import SSMTWorkItem
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.common_experiments import get_model1_templated_experiment
from idmtools_test.utils.decorators import warn_amount_ssmt_image_decorator
from idmtools_test.utils.utils import get_case_name

IDMTOOLS_COMPS_TEST_USE_CACHE_DATA = os.environ.get('IDMTOOLS_COMPS_TEST_USE_CACHE_DATA', 'on') in TRUTHY_VALUES
INPUT_FILE_PATH = Path(__file__).parent.joinpath("inputs")

logger = getLogger(__name__)


def find_comps_object_by_name_less_than_n_minutes(name, comps_object, idmtools_object, minutes=10, successful=True):
    """
    Fetching comps object by name

    Args:
        name: Name of item
        comps_object:COMPS Object type
        idmtools_object: Idmtools object
        minutes: Minutes since run suite was ran to consider valid
        successful: Only return successful

    Returns:
        Experiment
    """
    if IDMTOOLS_COMPS_TEST_USE_CACHE_DATA:
        logger.warning("USING COMPS caching")
        children = ['tags', 'files'] if comps_object == COMPSWorkItem else ['configuration', 'tags']
        qc = QueryCriteria().select_children(children).where([f'name={name}']).orderby('date_created desc')
        if comps_object == COMPSWorkItem:
            qc.select(['name', 'id', 'asset_collection_id', 'environment_name', 'date_created', 'state'])
        es = comps_object.get(query_criteria=qc)
        current_time = datetime.now(timezone.utc)
        idx = 0
        while len(es) and idx < len(es):
            sec_dif = (current_time - es[idx].date_created).seconds
            if 0 < sec_dif < minutes * 60:
                e = idmtools_object.from_id(es[idx].id)
                if e.succeeded or not successful:
                    logger.warning(f"Re-using {e.id} created at {es[idx].date_created} ({sec_dif / 60}m ago)")
                    return e
            idx += 1
    return None


def find_comps_experiment_by_name_less_than_n_minutes(exp_name, minutes=10, successful=True):
    """
    Fetching experiments by name

    Args:
        exp_name: Experiment name
        minutes: Minutes since run suite was ran to consider valid
        successful:

    Returns:
        Experiment
    """
    return find_comps_object_by_name_less_than_n_minutes(exp_name, COMPSExperiment, Experiment, minutes, successful)


def find_comps_suite_by_name_less_than_n_minutes(suite_name, minutes=10, successful=True):
    """
    Fetching Suite by name

    Args:
        suite_name: Suite name
        minutes: Minutes since run suite was ran to consider valid
        successful:

    Returns:
        Experiment
    """
    return find_comps_object_by_name_less_than_n_minutes(suite_name, COMPSSuite, Suite, minutes, successful)


def find_comps_workitem_by_name_less_than_n_minutes(work_item_name, minutes=10, successful=True):
    """
    Fetching WorkItem by name

    Args:
        work_item_name: WorkItem name
        minutes: Minutes since run suite was ran to consider valid
        successful:

    Returns:
        WorkItem
    """
    return find_comps_object_by_name_less_than_n_minutes(work_item_name, COMPSWorkItem, GenericWorkItem, minutes, successful)


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


def run_python_files_and_assets_slurm2(platform: Platform):
    """
    Run python model1.py in a suite with two experiments that each sweep a and b

    Args:
        platform: Platform to run it on

    Returns:
        Python Suite with two experiments

    Notes:
        This suite can be used for testing file fetching, analyzers, python models, suites, and more
    """
    # get the last time we ran this. If it is within last 5 minutes, reuse
    case_name = get_case_name(f'test_model1_files_and_assets_{platform.environment}')
    s = Suite(name=case_name)
    existing_s = find_comps_suite_by_name_less_than_n_minutes(case_name)
    if existing_s:
        return existing_s
    # create two experiments for each of these different ranges
    for range_a, range_b in [
        ((0, 2), [i * i for i in range(1, 4, 2)]),
        ((3, 5), [i * i for i in range(5, 8, 2)])
    ]:
        e = get_model1_templated_experiment(case_name)
        builder = SimulationBuilder()
        # ------------------------------------------------------
        # Sweeping parameters:
        # first way to sweep parameter 'a' is to use param_update function
        builder.add_sweep_definition(
            JSONConfiguredPythonTask.set_parameter_partial("a"),
            list(range_a)
        )

        # second way to sweep parameter 'b' is to use class setParam which basically doing same thing as param_update
        # method
        builder.add_sweep_definition(
            JSONConfiguredPythonTask.set_parameter_partial("b"),
            [i * i for i in range_b]
        )
        # ------------------------------------------------------
        e.simulations.add_builder(builder)
        s.add_experiment(e)

    s.run(platform=platform, wait_on_done=True)
    assert s.succeeded is True
    for e in s.experiments:
        assert e.succeeded
    return s


def create_python_asset_collection(platform):
    # Get an existing asset collection (first create it for the test)
    assets_path = Path(COMMON_INPUT_PATH, "python", "Assets")
    ac = AssetCollection.from_directory(assets_directory=assets_path)
    items = platform.create_items([ac])
    assert 1 == len(items)
    assert isinstance(items[0], AssetCollection)
    comps_ac_id = ac.uid
    # Then get an "existing asset" to use for the experiment
    return platform.get_item(comps_ac_id, item_type=ItemType.ASSETCOLLECTION, raw=False)


@pytest.fixture
def python_ac_on_slurm2(platform_slurm_2):
    """
    Create AC on Slurm2

    Args:
        platform_slurm_2: Slurm 2

    Returns:
        Suite
    """
    return create_python_asset_collection(platform_slurm_2)


@pytest.fixture
def python_ac_on_comp2(platform_comps2):
    """
    Create AC on comp2

    Args:
        platform_comps2: comp2

    Returns:
        Suite
    """
    return create_python_asset_collection(platform_comps2)


@pytest.fixture
def python_files_and_assets_slurm2(platform_slurm_2):
    """
    Run Python model 1 suite on slurm2

    Args:
        platform_slurm_2: Slurm 2

    Returns:
        Suite
    """
    return run_python_files_and_assets_slurm2(platform_slurm_2)


@pytest.fixture
def python_files_and_assets_comps2(platform_comps2):
    """
    Run python model1.py suite on COMPS 2
    Args:
        platform_comps2: Comps2

    Returns:
        Suite
    """
    return run_python_files_and_assets_slurm2(platform_comps2)


@pytest.fixture
@warn_amount_ssmt_image_decorator
def ssmt_workitem_python_hello(platform_slurm_2):
    name = get_case_name('ssmt_workitem_python_hello')
    ewi = find_comps_workitem_by_name_less_than_n_minutes(name)
    if ewi:
        return ewi

    command = "python3 Assets/hello.py"
    user_files = AssetCollection()
    user_files.add_asset(INPUT_FILE_PATH.joinpath("hello.py"))

    # Build our work-item
    wi = SSMTWorkItem(
        name=name, command=command, assets=user_files,
        tags={'idmtools': name, 'WorkItem type': 'Docker'}
    )
    wi.run(wait_on_done=True, platform=platform_slurm_2)

    # we just assert it is true here. Other tests cover detail functionlaity of workitems
    assert wi.succeeded
    return wi

@pytest.fixture
def create_experiment_no_asset(platform_comps2):
    case_name = get_case_name("test_experiment_operations.py--test_no_assets")
    existing_experiment = find_comps_experiment_by_name_less_than_n_minutes(case_name)
    if existing_experiment:
        return existing_experiment
    bt = CommandTask("Assets\\hello_world.bat")
    experiment = Experiment.from_task(
        bt,
        name=case_name,
        tags=dict(
            test_type='No Assets'
        )
    )
    experiment.add_asset(Asset(content="echo Hello World", filename='hello_world.bat'))

    experiment.run(wait_until_done=True, platform=platform_comps2)
    if not experiment.succeeded:
        raise ValueError("Setup prep failed")
    return experiment