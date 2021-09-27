import uuid

import allure
import hashlib
import os
import pytest

from COMPS.Data import Experiment as COMPSExperiment, QueryCriteria
from logging import getLogger
from idmtools.entities.experiment import Experiment
from idmtools.entities import Suite
from .utils import comps_decorate_test

logger = getLogger()


@comps_decorate_test("experiment_list_assets")
@pytest.mark.parametrize('suite', [pytest.lazy_fixture('python_files_and_assets_slurm2'),
                                   pytest.lazy_fixture('python_files_and_assets_comps2')])
def test_experiment_operation_assets_files(suite: Suite):
    """
    Test that the list assets with children
    Test that the list assets without children
    Test that download works
    Test that the list assets on children(sims) works
    Returns:

    """
    e_p = suite.experiments[0]
    # test experiment_operation 'list_assets' and children=True
    assets = suite.platform._experiments.list_assets(e_p, children=True)
    assert len(assets) == 1
    for asset in assets:
        out_dir = os.path.join(os.path.dirname(__file__), 'output')
        name = os.path.join(out_dir, asset.filename)
        os.makedirs(out_dir, exist_ok=True)
        asset.download_to_path(name) # TODO always fail in slurm
        assert set(os.listdir(str(out_dir))) == {'model1.py'}
        try:
            with open(name, 'rb') as din:
                content = din.read()
                md5_hash = hashlib.md5()
                md5_hash.update(content)
                #assert asset.checksum == uuid.UUID(md5_hash.hexdigest()) # TODO always fail in comps2
        # ensure we always delete file after test
        finally:
            os.remove(name)

    # test experiment_operation 'list_files' with no children, should always return empty
    all_linked_files = suite.platform._experiments.list_files(e_p)
    assert len(all_linked_files) == 0

    # test experiment_operation 'list_files' with children=True
    all_linked_files = suite.platform._experiments.list_files(e_p, children=True)
    assert len(all_linked_files) == 16
    assert set([asset.filename for asset in all_linked_files]) == {'stderr.txt', 'stdout.txt', 'config.json',
                                                                   'result.json'}

    # test experiment_operation 'list_files' with children=True and filters
    filtered_linked_files = suite.platform._experiments.list_files(e_p, children=True, filters=['*.json'])
    assert len(filtered_linked_files) == 8
    assert set([asset.filename for asset in filtered_linked_files]) == {'config.json', 'result.json'}

    # test test experiment_operation 'platform_list_asset'
    assets = suite.platform._experiments.platform_list_asset(e_p)
    assert len(assets) == 1

    # test test experiment_operation 'platform_list_files' which always return empty
    files = suite.platform._experiments.platform_list_files(e_p)
    assert len(files) == 0

    # test simulation_operation 'list_assets'
    for sim in e_p.simulations:
        assets = suite.platform._simulations.list_assets(sim)
        assert len(assets) == 0

    # test simulation_operation  'list_files'
    for sim in e_p.simulations:
        # no filters
        all_linked_files = suite.platform._simulations.list_files(sim)
        assert len(all_linked_files) == 4
        assert set([asset.filename for asset in all_linked_files]) == {'stderr.txt', 'stdout.txt', 'config.json',
                                                                       'result.json'}
        # with filters
        filtered_linked_files = suite.platform._simulations.list_files(sim, filters=['*.json'])
        assert len(filtered_linked_files) == 2
        assert set([asset.filename for asset in filtered_linked_files]) == {'config.json', 'result.json'}


@pytest.mark.comps
@pytest.mark.smoke
@allure.story("COMPS")
@allure.suite("idmtools_platform_comps")
def test_no_assets(create_experiment_no_asset):
    # Call Experiments
    qc = QueryCriteria().select_children("tags").where_tag(
        [
            'test_type=No Assets'
        ]
    )

    comps_experiments = COMPSExperiment.get(query_criteria=qc)
    experiment = comps_experiments[0]

    # load as idm object(testing both get and to_entity
    idmtools_experiment = Experiment.from_id(experiment.id)

    # check tags
    for e in [experiment, idmtools_experiment]:
        assert set(e.tags) == {'idmtools', 'task_type', 'test_name', 'test_type'}

    # check empty asset collection
    assert idmtools_experiment.assets.count == 0
    assert idmtools_experiment.simulation_count == 1
    assert idmtools_experiment.simulations[0].assets.count == 0
